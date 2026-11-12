<!-- source: DeepWiki mcp.deepwiki.com · repo miurla/babyagi-ui · page 7 Examples and Usage · fetched 2026-10-27 -->

# Examples and Usage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/Agent/FirstTimeMessage.tsx](src/components/Agent/FirstTimeMessage.tsx)
- [src/pages/example/headless/index.tsx](src/pages/example/headless/index.tsx)
- [src/pages/example/ui/index.tsx](src/pages/example/ui/index.tsx)

</details>



This document provides practical examples and usage patterns for the BabyAGI-UI system. It demonstrates how to interact with and integrate the autonomous agent capabilities in both full UI and headless/minimal contexts. For information about customizing or extending BabyAGI-UI, see [Development and Customization](#8).

## Usage Patterns Overview

BabyAGI-UI can be used in two primary ways:

1. **Full UI Mode** - Utilizing the complete user interface with agent blocks, task visualization, and interactive configuration.
2. **Headless Mode** - Using BabyAGI-UI with minimal UI components for custom integrations or simplified interfaces.

The following diagram illustrates how the examples connect to the agent system:

```mermaid
graph TD
    subgraph "Usage Patterns"
        UI["Full UI Example"]
        Headless["Headless Example"]
    end
    
    subgraph "Agent System"
        useAgent["useAgent Hook"]
        API["Agent API Endpoint"]
        Agents["Agent Executors"]
    end
    
    UI -->|"uses"| useAgent
    Headless -->|"uses"| useAgent
    useAgent -->|"calls"| API
    API -->|"initializes"| Agents
    
    subgraph "Message Processing"
        AM["agentMessages Array"]
        GM["groupMessages Function"]
        Blocks["Agent Blocks"]
    end
    
    useAgent -->|"returns"| AM
    AM -->|"processed by"| GM
    GM -->|"creates"| Blocks
    UI -->|"renders"| Blocks
    Headless -->|"renders raw"| AM
```

Sources: [src/pages/example/ui/index.tsx](), [src/pages/example/headless/index.tsx]()

## UI Example

The UI example demonstrates how to integrate BabyAGI-UI with a richer user interface experience, including properly formatted agent blocks for better visualization.

```mermaid
sequenceDiagram
    participant User
    participant UIExample as "ExampleUIPage"
    participant AgentHook as "useAgent Hook"
    participant MessageUtils as "groupMessages"
    participant Components as "AgentBlock Component"
    participant API as "Agent API"

    User->>UIExample: Input objective
    UIExample->>AgentHook: Call useAgent({api, agentId})
    AgentHook->>API: Submit objective
    API-->>AgentHook: Stream agent messages
    AgentHook-->>UIExample: Update agentMessages array
    UIExample->>MessageUtils: groupMessages(agentMessages, isRunning)
    MessageUtils-->>UIExample: Return formatted blocks
    UIExample->>Components: Render AgentBlock components
    Components-->>User: Display formatted agent output
```

### UI Example Implementation

The UI example uses the `useAgent` hook to connect to the agent system and the `groupMessages` utility to format the agent messages into blocks for display:

1. The component initializes the agent connection with the `useAgent` hook
2. Agent messages are processed with `groupMessages` to create structured blocks
3. The blocks are rendered using the `AgentBlock` component

Key code:

[src/pages/example/ui/index.tsx:9-18]()

This example provides a more sophisticated UI with formatted agent blocks, making it suitable for applications where visual presentation is important.

Sources: [src/pages/example/ui/index.tsx]()

## Headless Example

The headless example demonstrates a minimal integration of BabyAGI-UI, suitable for custom interfaces or when you want to handle the presentation layer yourself.

```mermaid
sequenceDiagram
    participant User
    participant HeadlessExample as "ExampleHeadlessPage"
    participant AgentHook as "useAgent Hook"
    participant API as "Agent API"

    User->>HeadlessExample: Input objective
    HeadlessExample->>AgentHook: Call useAgent({api, agentId})
    AgentHook->>API: Submit objective
    API-->>AgentHook: Stream agent messages
    AgentHook-->>HeadlessExample: Update agentMessages array
    HeadlessExample-->>User: Display raw agent messages
```

### Headless Example Implementation

The headless example directly renders the raw agent messages without additional formatting:

1. The component initializes the agent connection with the `useAgent` hook
2. Agent messages are rendered directly in a simple format
3. No additional message processing or formatting is applied

Key code:

[src/pages/example/headless/index.tsx:5-8]()

[src/pages/example/headless/index.tsx:18-22]()

This approach is ideal for:
- Custom integrations where you want to handle message formatting yourself
- Simpler applications that don't need the full UI components
- Headless or API-only services that use BabyAGI-UI's agent capabilities

Sources: [src/pages/example/headless/index.tsx]()

## Common Elements Between Examples

Both the UI and headless examples share certain common elements:

```mermaid
graph TD
    subgraph "Common Elements"
        useAgent["useAgent Hook"]
        Input["Input Field"]
        Form["Form Submission"]
        FTUM["FirstTimeUserMessage"]
    end
    
    subgraph "UI Example Specific"
        AgentBlock["AgentBlock Component"]
        groupMessages["groupMessages Function"]
        Blocks["Structured Block Array"]
    end
    
    subgraph "Headless Example Specific"
        RawMessages["Raw agentMessages Rendering"]
    end
    
    useAgent --> |"provides"| agentMessages["agentMessages Array"]
    useAgent --> |"provides"| input["input Value"]
    useAgent --> |"provides"| handleSubmit["handleSubmit Function"]
    useAgent --> |"provides"| handleInputChange["handleInputChange Function"]
    useAgent --> |"provides"| isRunning["isRunning State"]
    
    Form --> handleSubmit
    Input --> input
    Input --> handleInputChange
    
    agentMessages --> RawMessages
    agentMessages --> groupMessages
    groupMessages --> Blocks
    Blocks --> AgentBlock
```

Sources: [src/pages/example/ui/index.tsx](), [src/pages/example/headless/index.tsx](), [src/components/Agent/FirstTimeMessage.tsx]()

### The useAgent Hook

The core of both examples is the `useAgent` hook, which provides:

- Connection to the agent API
- Management of the input state
- Handling form submission
- Processing and streaming agent messages

Usage pattern:

```jsx
const { 
  agentMessages,  // Array of messages from the agent
  input,          // Current input field value
  handleSubmit,   // Function to handle form submission
  handleInputChange, // Function to handle input changes
  isRunning       // Boolean indicating if the agent is running
} = useAgent({
  api: '/api/agent',   // API endpoint for the agent
  agentId: 'babydeeragi' // ID of the agent to use
});
```

This pattern is identical in both examples, showing how the `useAgent` hook provides a consistent interface regardless of the UI approach.

Sources: [src/pages/example/ui/index.tsx:9-13](), [src/pages/example/headless/index.tsx:5-8]()

## Usage Scenarios

Here are some common usage scenarios for BabyAGI-UI:

| Scenario | Recommended Approach | Agent Type | Notes |
|----------|---------------------|------------|-------|
| Research task with multiple subtasks | Full UI | BabyDeerAGI | Best for visualizing complex task hierarchies |
| Simple query processing | Headless | BabyAGI | Minimal interface for straightforward queries |
| Web research with integrated search | Full UI | BabyBeeAGI | Visualize search results and agent reasoning |
| Tool-using workflows | Full UI | BabyElfAGI | See which skills the agent is using for each task |
| Integration into existing applications | Headless | Any | Customize the presentation layer while leveraging BabyAGI capabilities |
| Interactive user guidance | Full UI | BabyDeerAGI | Leverage user input capabilities with clear task visualization |

### Implementation Considerations

When implementing BabyAGI-UI in your own applications, consider:

1. **API Endpoint**: Both examples use `/api/agent` as the endpoint, but you can configure this to point to a custom endpoint.
2. **Agent Type**: The examples use 'babydeeragi', but you can select any of the available agent types.
3. **UI Components**: For full UI applications, leverage the `AgentBlock` component and `groupMessages` utility.
4. **First-time User Experience**: Both examples include the `FirstTimeUserMessage` component to guide new users.

Sources: [src/pages/example/ui/index.tsx](), [src/pages/example/headless/index.tsx](), [src/components/Agent/FirstTimeMessage.tsx]()

## Custom Implementation Example

Here's a diagram showing how you might implement a custom UI that combines elements from both examples:

```mermaid
graph TD
    subgraph "Custom Implementation"
        MyComponent["MyCustomAgentComponent"]
        CustomUI["Custom UI Elements"]
        AgentIntegration["BabyAGI Integration"]
    end
    
    subgraph "BabyAGI-UI Core"
        useAgent["useAgent Hook"]
        API["Agent API"]
        Message["Message Processing"]
    end
    
    MyComponent -->|"initializes"| AgentIntegration
    AgentIntegration -->|"uses"| useAgent
    useAgent -->|"calls"| API
    API -->|"returns"| useAgent
    useAgent -->|"updates"| AgentIntegration
    Message -->|"formats"| AgentIntegration
    AgentIntegration -->|"updates"| CustomUI
    CustomUI -->|"renders in"| MyComponent
```

This pattern allows you to:

1. Use the core agent capabilities through the `useAgent` hook
2. Implement custom UI components for presentation
3. Select which message processing utilities to use
4. Create a tailored user experience while leveraging BabyAGI-UI's agent capabilities

The key is to leverage the `useAgent` hook as the bridge between your custom UI and the BabyAGI-UI agent system.

Sources: [src/pages/example/ui/index.tsx](), [src/pages/example/headless/index.tsx]()

---

