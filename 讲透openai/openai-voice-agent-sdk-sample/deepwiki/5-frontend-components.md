<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-voice-agent-sdk-sample · page 5 Frontend Components · fetched 2026-10-26 -->

# Frontend Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/components/Composer.tsx](frontend/src/components/Composer.tsx)
- [frontend/src/components/Header.tsx](frontend/src/components/Header.tsx)
- [frontend/src/components/messages/TextMessage.tsx](frontend/src/components/messages/TextMessage.tsx)

</details>



This page provides an overview of the key frontend components that make up the user interface of the OpenAI Voice Agent SDK Sample App. It describes the main React components, their responsibilities, and how they interact within the Next.js application. For detailed information about specific components, see the respective subpages: [Header Component](#5.1), [Composer Component](#5.2), and [TextMessage Component](#5.3).

## Component Architecture

The frontend of the application is built using React within a Next.js framework. The components are organized in a hierarchical structure that manages different aspects of the user interface, from conversation display to user input handling.

```mermaid
graph TD
    App["App"] --> Layout["Layout"]
    Layout --> Header["Header"]
    Layout --> Conversation["Conversation"]
    Layout --> Composer["Composer"]
    
    Conversation --> Messages["Messages Container"]
    Messages --> TextMessage["TextMessage"]
    Messages --> ToolCall["ToolCall"]
    
    Composer --> TextInput["Text Input"]
    Composer --> AudioChat["Audio Chat Controls"]
    
    Header --> Logo["Logo"]
    Header --> AgentNameDisplay["Agent Name Display"]
    Header --> AudioPlayback["Audio Playback"]
    Header --> ResetButton["Reset Conversation Button"]
```

Sources: [frontend/src/components/Header.tsx](), [frontend/src/components/Composer.tsx](), [frontend/src/components/messages/TextMessage.tsx]()

## Core Components

### Header Component

The Header component appears at the top of the application and provides application context and controls.

```mermaid
classDiagram
    class Header {
        +string agentName
        +number[] playbackFrequencies
        +function stopPlaying()
        +function resetConversation()
        -renderLogo()
        -renderAgentName()
        -renderAudioPlayback()
        -renderResetButton()
    }
    
    Header --> AudioPlayback
    Header --> Button
    
    class AudioPlayback {
        +number[] playbackFrequencies
        +string itemClassName
        +number height
    }
    
    class Button {
        +string variant
        +string size
        +function onClick()
    }
```

The Header component includes:
- OpenAI logo
- Agent name display with animation
- Audio visualization during playback
- Reset button for starting new conversations

Sources: [frontend/src/components/Header.tsx:12-127]()

### Composer Component

The Composer component handles user input, allowing users to enter messages through text or voice.

```mermaid
classDiagram
    class Composer {
        +string prompt
        +function setPrompt()
        +function onSubmit()
        +boolean isLoading
        +ReactNode audioChat
        -useRef textareaRef
    }
    
    Composer --> Button
    Composer --> TextArea
    
    class TextArea {
        +string value
        +function onChange()
        +function onKeyDown()
    }
    
    class Button {
        +string variant
        +string size
        +boolean disabled
        +function onClick()
    }
```

Key features:
- Auto-expanding textarea for text input
- Enter key submission handling
- Integration point for audio chat functionality
- Submit button with appropriate disabled states

Sources: [frontend/src/components/Composer.tsx:6-65]()

### TextMessage Component

The TextMessage component renders individual messages in the conversation, supporting both user and agent messages.

```mermaid
classDiagram
    class TextMessage {
        +string text
        +boolean isUser
    }
    
    TextMessage --> ReactMarkdown
    ReactMarkdown --> CustomLink
    
    class ReactMarkdown {
        +object components
    }
    
    class CustomLink {
        +string href
        +ReactNode children
    }
```

Key features:
- Different styling for user and agent messages
- Markdown rendering for rich text formatting
- Custom link styling
- Responsive layout with appropriate spacing

Sources: [frontend/src/components/messages/TextMessage.tsx:5-42]()

## Component Data Flow

The following diagram illustrates how data flows between the frontend components during a typical conversation:

```mermaid
sequenceDiagram
    participant User
    participant Composer as "Composer"
    participant App as "App State"
    participant Conversation as "Conversation"
    participant TextMessage as "TextMessage"
    participant Header as "Header"
    participant Backend as "Backend (WebSocket)"
    
    User->>Composer: Types or speaks message
    Composer->>App: Submits message
    App->>Backend: Sends message
    App->>Conversation: Updates with user message
    Conversation->>TextMessage: Renders user message
    
    Backend-->>App: Streams response
    App->>Conversation: Updates with agent message
    Conversation->>TextMessage: Renders agent message
    App->>Header: Updates audio state
    Header-->>User: Displays audio visualizer
```

Sources: [frontend/src/components/Composer.tsx](), [frontend/src/components/Header.tsx](), [frontend/src/components/messages/TextMessage.tsx]()

## Component Responsibilities

Each frontend component has specific responsibilities within the application:

| Component | Primary Responsibility | Key Props | Interactions |
|-----------|------------------------|-----------|--------------|
| Header | Display application context and controls | `agentName`, `playbackFrequencies`, `stopPlaying`, `resetConversation` | Audio playback visualization, New conversation creation |
| Composer | Handle user input (text and audio) | `prompt`, `setPrompt`, `onSubmit`, `isLoading`, `audioChat` | Text input, Audio recording, Message submission |
| TextMessage | Display conversation messages | `text`, `isUser` | Markdown rendering, Link formatting |
| Conversation | Manage message display and scrolling | `messages` | Rendering message components, Auto-scrolling |
| ToolCall | Display tool/function calls made by the agent | `toolCall`, `result` | Showing function execution details |

Sources: [frontend/src/components/Header.tsx](), [frontend/src/components/Composer.tsx](), [frontend/src/components/messages/TextMessage.tsx]()

## UI Layout and Styling

The application follows a vertical layout structure typical of chat applications, with components stacked to provide a natural conversation flow:

```mermaid
graph TD
    subgraph "UI Layout"
        Header["Header (Top)"]
        Conversation["Conversation (Middle)"]
        Composer["Composer (Bottom)"]
    end
    
    Header --> Conversation
    Conversation --> Composer
    
    subgraph "Conversation Content"
        UserMessage["User Messages (Right-aligned)"]
        AgentMessage["Agent Messages (Left-aligned)"]
        ToolCallBlock["Tool Calls (Left-aligned)"]
    end
    
    Conversation --- UserMessage
    Conversation --- AgentMessage
    Conversation --- ToolCallBlock
```

The UI uses:
- Rounded corners for messages and input components
- Different background colors to distinguish user and agent messages
- Custom styling for interactive elements like buttons
- Responsive design to adapt to different screen sizes
- Animations for transitions and audio visualization

Sources: [frontend/src/components/Header.tsx](), [frontend/src/components/Composer.tsx](), [frontend/src/components/messages/TextMessage.tsx]()

## Component Props Interface

The following diagram illustrates the props interfaces for the main components, showing how they connect to the application state:

```mermaid
classDiagram
    class AppState {
        +string[] messages
        +string currentPrompt
        +boolean isLoading
        +string agentName
        +number[] audioFrequencies
        +function setPrompt()
        +function sendMessage()
        +function resetConversation()
        +function stopAudio()
    }
    
    AppState --> HeaderProps
    AppState --> ComposerProps
    AppState --> ConversationProps
    
    class HeaderProps {
        +string agentName
        +number[] playbackFrequencies
        +function stopPlaying()
        +function resetConversation()
    }
    
    class ComposerProps {
        +string prompt
        +function setPrompt()
        +function onSubmit()
        +boolean isLoading
        +ReactNode audioChat
    }
    
    class ConversationProps {
        +object[] messages
    }
    
    ConversationProps --> TextMessageProps
    
    class TextMessageProps {
        +string text
        +boolean isUser
    }
```

Sources: [frontend/src/components/Header.tsx:12-22](), [frontend/src/components/Composer.tsx:6-12](), [frontend/src/components/messages/TextMessage.tsx:20-23]()

## Integration with Audio Features

The components work together to provide a seamless voice chat experience:

- The Header component displays audio visualizations during playback
- The Composer component integrates audio recording controls
- The application manages audio state transitions between components

The audio integration connects through props and state management to ensure synchronized behavior across the UI.

Sources: [frontend/src/components/Header.tsx:53-56](), [frontend/src/components/Composer.tsx:51]()

This overview page provides a foundation for understanding the frontend component architecture. For more detailed information about specific components, see the subpages on [Header Component](#5.1), [Composer Component](#5.2), and [TextMessage Component](#5.3).

---

