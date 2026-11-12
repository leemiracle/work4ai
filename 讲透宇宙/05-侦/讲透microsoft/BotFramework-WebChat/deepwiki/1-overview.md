<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/BotFramework-WebChat · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [packages/api/package.json](packages/api/package.json)
- [packages/bundle/package.json](packages/bundle/package.json)
- [packages/component/package.json](packages/component/package.json)
- [packages/core/package.json](packages/core/package.json)
- [packages/directlinespeech/package.json](packages/directlinespeech/package.json)
- [packages/embed/servicingPlan.json](packages/embed/servicingPlan.json)
- [packages/playground/package.json](packages/playground/package.json)
- [samples/index.html](samples/index.html)

</details>



## Purpose and Scope

BotFramework-WebChat is a highly-customizable web-based chat client for the Microsoft Bot Framework v4 SDK. This system enables developers to embed conversational AI experiences into web applications through multiple integration methods, from simple CDN inclusion to full React component customization.

This document covers the overall architecture, package structure, and core systems of the Web Chat codebase. For specific integration patterns, see [Integration Guide](#5). For detailed feature documentation, see [Key Features](#4). For development workflows, see [Development](#6).

## High-Level Architecture

The Web Chat system is architected as a modular monorepo with distinct layers handling different concerns:

```mermaid
graph TB
    subgraph "Distribution Layer"
        CDN["webchat.js CDN Bundle"]
        NPM["NPM Packages"]
        Embed["iframe Embed"]
    end
    
    subgraph "Integration Layer"
        Bundle["botframework-webchat"]
        API["botframework-webchat-api"]
    end
    
    subgraph "UI Layer"
        Component["botframework-webchat-component"]
        Styles["botframework-webchat-styles"]
        FluentTheme["botframework-webchat-fluent-theme"]
    end
    
    subgraph "State Layer"
        Core["botframework-webchat-core"]
        Redux["Redux Store"]
        Sagas["Redux Sagas"]
    end
    
    subgraph "Protocol Layer"
        DirectLine["Direct Line Protocol"]
        DirectLineSpeech["botframework-directlinespeech-sdk"]
        SpeechServices["Speech Integration"]
    end
    
    subgraph "Utility Layer"
        Base["botframework-webchat-base"]
        IsomorphicReact["isomorphic-react"]
        TestHarness["Test Infrastructure"]
    end
    
    CDN --> Bundle
    NPM --> Bundle
    Embed --> CDN
    
    Bundle --> API
    Bundle --> Component
    
    API --> Core
    Component --> Core
    Component --> Styles
    
    Core --> Redux
    Core --> Sagas
    Core --> DirectLine
    
    DirectLineSpeech --> SpeechServices
    Component --> DirectLineSpeech
    
    FluentTheme --> Component
    
    Base --> Core
    Base --> Component
    IsomorphicReact --> Component
```

Sources: [package.json:17-34](), [README.md:1-391](), [packages/bundle/package.json:61-68](), [packages/component/package.json:71-75]()

## Package Structure

The monorepo is organized using npm workspaces with packages serving distinct architectural roles:

| Package | Purpose | Key Dependencies |
|---------|---------|------------------|
| `botframework-webchat` | Main distribution bundle | component, core, api |
| `botframework-webchat-api` | Public API surface | core |
| `botframework-webchat-component` | React UI components | api, core, styles |
| `botframework-webchat-core` | State management | Redux, redux-saga |
| `botframework-webchat-styles` | CSS framework | - |
| `botframework-directlinespeech-sdk` | Speech channel | microsoft-cognitiveservices-speech-sdk |
| `botframework-webchat-fluent-theme` | Fluent UI theme pack | component |

The dependency hierarchy follows a strict layering where higher-level packages depend on lower-level ones but not vice versa.

```mermaid
graph TD
    WebApp["Web Applications"]
    
    WebApp --> Bundle["botframework-webchat"]
    WebApp --> API["botframework-webchat-api"]
    
    Bundle --> Component["botframework-webchat-component"]
    Bundle --> Core["botframework-webchat-core"]
    Bundle --> DirectLineSpeech["botframework-directlinespeech-sdk"]
    
    API --> Core
    Component --> API
    Component --> Styles["botframework-webchat-styles"]
    
    Core --> Base["botframework-webchat-base"]
    Component --> Base
    
    FluentTheme["botframework-webchat-fluent-theme"] --> Component
```

Sources: [package.json:17-34](), [packages/bundle/package.json:116-143](), [packages/component/package.json:141-168](), [packages/core/package.json:110-119]()

## Core Systems

### State Management Architecture

Web Chat uses Redux with redux-saga for state management, providing a unidirectional data flow:

```mermaid
graph LR
    subgraph "External Events"
        DirectLineActivity["Direct Line Activities"]
        UserInput["User Input"]
        APICall["API Calls"]
    end
    
    subgraph "Redux Store"
        Actions["Actions"]
        Reducers["Reducers"]
        State["Application State"]
    end
    
    subgraph "Side Effects"
        Sagas["Redux Sagas"]
        DirectLineSDK["Direct Line SDK"]
        SpeechSDK["Speech SDK"]
    end
    
    subgraph "UI Layer"
        ReactComponents["React Components"]
        Hooks["Custom Hooks"]
    end
    
    DirectLineActivity --> Actions
    UserInput --> Actions
    APICall --> Actions
    
    Actions --> Reducers
    Reducers --> State
    Actions --> Sagas
    
    Sagas --> DirectLineSDK
    Sagas --> SpeechSDK
    Sagas --> Actions
    
    State --> ReactComponents
    ReactComponents --> Hooks
    Hooks --> Actions
```

Sources: [packages/core/package.json:110-119](), [CHANGELOG.md:261-288]()

### Component Architecture

The UI is built with React components following a provider pattern for context and hooks for state access:

```mermaid
graph TB
    subgraph "Component Hierarchy"
        WebChatComposer["WebChatComposer"]
        BasicWebChat["BasicWebChat"]
        
        subgraph "Core Components"
            BasicTranscript["BasicTranscript"]
            BasicSendBox["BasicSendBox"]
            BasicToaster["BasicToaster"]
        end
        
        subgraph "Activity Rendering"
            ActivityRenderer["ActivityRenderer"]
            AttachmentRenderer["AttachmentRenderer"]
            MiddlewareProvider["MiddlewareProvider"]
        end
        
        subgraph "Custom Hooks"
            useActivities["useActivities"]
            useSendMessage["useSendMessage"]
            useStyleOptions["useStyleOptions"]
        end
    end
    
    WebChatComposer --> BasicWebChat
    BasicWebChat --> BasicTranscript
    BasicWebChat --> BasicSendBox
    BasicWebChat --> BasicToaster
    
    BasicTranscript --> ActivityRenderer
    ActivityRenderer --> AttachmentRenderer
    ActivityRenderer --> MiddlewareProvider
    
    BasicSendBox --> useActivities
    BasicSendBox --> useSendMessage
    BasicWebChat --> useStyleOptions
```

Sources: [packages/component/package.json:141-168](), [CHANGELOG.md:246-250]()

## Integration Methods

Web Chat supports three primary integration patterns:

### CDN Integration

Direct inclusion via script tag with global `WebChat` object:

```mermaid
graph LR
    CDN["cdn.botframework.com"] --> ScriptTag["<script> tag"]
    ScriptTag --> GlobalWebChat["window.WebChat"]
    GlobalWebChat --> renderWebChat["renderWebChat()"]
    GlobalWebChat --> createDirectLine["createDirectLine()"]
```

### React Integration

Import as ES modules or CommonJS for full customization:

```mermaid
graph LR
    NPM["npm install"] --> Import["import ReactWebChat"]
    Import --> ReactComponent["<ReactWebChat />"]
    ReactComponent --> Hooks["useWebChat hooks"]
    ReactComponent --> CustomComponents["Custom Components"]
```

### iframe Embed

Hosted solution with minimal configuration:

```mermaid
graph LR
    EmbedURL["webchat.botframework.com"] --> iframe["<iframe>"]
    iframe --> HostedWebChat["Hosted Web Chat"]
    HostedWebChat --> ConfigAPI["Config API"]
```

Sources: [README.md:152-289](), [packages/embed/hostDevServer.mjs:1-38](), [packages/embed/servicingPlan.json:1-600]()

## Key Feature Systems

### Speech Integration

Web Chat provides multiple speech engines through a ponyfill architecture:

```mermaid
graph TB
    subgraph "Speech Sources"
        BrowserAPI["Web Speech API"]
        CognitiveServices["Azure Cognitive Services"]
        DirectLineSpeechChannel["Direct Line Speech"]
    end
    
    subgraph "Ponyfill Layer"
        PonyfillFactory["Ponyfill Factory"]
        SpeechRecognition["SpeechRecognition"]
        SpeechSynthesis["SpeechSynthesis"]
    end
    
    subgraph "Web Chat Integration"
        SpeechState["Speech State Management"]
        VoiceUI["Voice UI Components"]
        DictationMode["Dictation Mode"]
    end
    
    BrowserAPI --> PonyfillFactory
    CognitiveServices --> PonyfillFactory
    DirectLineSpeechChannel --> PonyfillFactory
    
    PonyfillFactory --> SpeechRecognition
    PonyfillFactory --> SpeechSynthesis
    
    SpeechRecognition --> SpeechState
    SpeechSynthesis --> SpeechState
    SpeechState --> VoiceUI
    SpeechState --> DictationMode
```

Sources: [packages/directlinespeech/package.json:112-123](), [CHANGELOG.md:358-372](), [README.md:356-372]()

### Theming and Customization

The styling system supports multiple customization levels:

```mermaid
graph LR
    subgraph "Style Sources"
        StyleOptions["styleOptions"]
        CSSVariables["CSS Variables"]
        CustomCSS["Custom CSS"]
        ThemePacks["Theme Packs"]
    end
    
    subgraph "Style Processing"
        StylesPackage["webchat-styles"]
        EmotionCSS["@emotion/css"]
        CSSInjection["CSS Injection"]
    end
    
    subgraph "Output"
        StyledComponents["Styled Components"]
        FluentTheme["Fluent Theme"]
        CustomThemes["Custom Themes"]
    end
    
    StyleOptions --> StylesPackage
    CSSVariables --> StylesPackage
    CustomCSS --> EmotionCSS
    ThemePacks --> EmotionCSS
    
    StylesPackage --> CSSInjection
    EmotionCSS --> CSSInjection
    
    CSSInjection --> StyledComponents
    CSSInjection --> FluentTheme
    CSSInjection --> CustomThemes
```

Sources: [CHANGELOG.md:49-78](), [packages/component/package.json:141-168](), [README.md:290-306]()

---

