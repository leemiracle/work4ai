<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/BotFramework-WebChat · page 5 Integration Guide · fetched 2026-10-26 -->

# Integration Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [samples/index.html](samples/index.html)

</details>



This document provides an overview of the three primary methods for integrating Bot Framework Web Chat into applications: JavaScript/CDN integration, React component integration, and iframe embedding. Each method offers different levels of customization and is suited for different technical requirements and use cases.

For detailed implementation guides for each method, see [React Integration](#5.1), [JavaScript/CDN Integration](#5.2), and [iframe Embed](#5.3). For information about customizing the Web Chat UI after integration, see [Key Features](#4).

## Integration Methods Overview

Bot Framework Web Chat supports three distinct integration approaches, each targeting different development scenarios and providing varying levels of customization capability.

### Integration Methods Comparison

| Integration Method | Package Source | Customization Level | Use Case |
|-------------------|----------------|-------------------|----------|
| JavaScript/CDN | `https://cdn.botframework.com/botframework-webchat/latest/webchat.js` | Moderate | Static websites, quick integration |
| React Components | `npm install botframework-webchat` | Full | React applications, custom components |
| iframe Embed | `webchat.botframework.com` | Limited | Third-party websites, sandboxed deployment |

### Integration Architecture

```mermaid
graph TB
    subgraph "Integration Methods"
        CDNMethod["JavaScript/CDN Integration"]
        ReactMethod["React Integration"]
        iFrameMethod["iframe Integration"]
    end
    
    subgraph "Distribution Sources"
        CDNSource["CDN Distribution<br/>cdn.botframework.com"]
        NPMSource["NPM Registry<br/>botframework-webchat"]
        EmbedService["Embed Service<br/>webchat.botframework.com"]
    end
    
    subgraph "Core APIs"
        RenderAPI["window.WebChat.renderWebChat()"]
        ReactComponent["ReactWebChat component"]
        URLParams["URL Parameters"]
    end
    
    subgraph "Authentication"
        DirectLineAPI["Direct Line API"]
        TokenGen["Token Generation"]
        SecretAuth["Secret Authentication"]
    end
    
    subgraph "Bot Services"
        BotFramework["Azure Bot Framework"]
        DirectLineChannel["Direct Line Channel"]
    end
    
    CDNMethod --> CDNSource
    ReactMethod --> NPMSource
    iFrameMethod --> EmbedService
    
    CDNSource --> RenderAPI
    NPMSource --> ReactComponent
    EmbedService --> URLParams
    
    RenderAPI --> DirectLineAPI
    ReactComponent --> DirectLineAPI
    URLParams --> DirectLineAPI
    
    DirectLineAPI --> TokenGen
    DirectLineAPI --> SecretAuth
    DirectLineAPI --> DirectLineChannel
    DirectLineChannel --> BotFramework
```

Sources: [README.md:152-257]()

### Code Entity Mapping

```mermaid
graph TB
    subgraph "JavaScript/CDN APIs"
        WindowWebChat["window.WebChat"]
        RenderWebChat["renderWebChat()"]
        CreateDirectLine["createDirectLine()"]
        WebChatJS["webchat.js bundle"]
    end
    
    subgraph "React APIs"
        ReactWebChatComp["ReactWebChat"]
        CreateDirectLineReact["createDirectLine"]
        BotframeworkWebchat["botframework-webchat package"]
        CreateStore["createStore()"]
        CreateStoreDevTools["createStoreWithDevTools()"]
    end
    
    subgraph "iframe APIs"
        EmbedURL["webchat.botframework.com"]
        URLParameters["URL query parameters"]
        PostMessage["postMessage API"]
    end
    
    subgraph "Common Interfaces"
        DirectLineConfig["DirectLine configuration"]
        StyleOptions["styleOptions"]
        UserConfig["userID, username, locale"]
    end
    
    WindowWebChat --> RenderWebChat
    WindowWebChat --> CreateDirectLine
    RenderWebChat --> DirectLineConfig
    RenderWebChat --> StyleOptions
    RenderWebChat --> UserConfig
    
    ReactWebChatComp --> DirectLineConfig
    ReactWebChatComp --> StyleOptions
    ReactWebChatComp --> UserConfig
    CreateDirectLineReact --> DirectLineConfig
    CreateStore --> ReactWebChatComp
    
    EmbedURL --> URLParameters
    URLParameters --> DirectLineConfig
    URLParameters --> StyleOptions
    PostMessage --> ReactWebChatComp
```

Sources: [README.md:208-218](), [README.md:243-251]()

## Authentication Flow

All integration methods require authentication with the Direct Line channel through either a secret or token-based approach. The recommended approach is token-based authentication for security reasons.

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant TokenService as "Token Service"
    participant WebChat as "Web Chat"
    participant DirectLine as "Direct Line API"
    participant Bot as "Azure Bot Service"
    
    Client->>TokenService: Request token with secret
    TokenService->>DirectLine: Exchange secret for token
    DirectLine->>TokenService: Return token
    TokenService->>Client: Return token
    Client->>WebChat: Initialize with token
    WebChat->>DirectLine: Connect with token
    DirectLine->>Bot: Establish conversation
    Bot->>DirectLine: Send activities
    DirectLine->>WebChat: Deliver activities
```

Sources: [README.md:154-170]()

## Quick Start Examples

### JavaScript/CDN Integration

The JavaScript integration method uses a global `window.WebChat` object provided by the CDN bundle:

```html
<script crossorigin="anonymous" 
        src="https://cdn.botframework.com/botframework-webchat/latest/webchat.js">
</script>
<script>
  window.WebChat.renderWebChat({
    directLine: window.WebChat.createDirectLine({
      token: 'YOUR_DIRECT_LINE_TOKEN'
    }),
    userID: 'YOUR_USER_ID'
  }, document.getElementById('webchat'));
</script>
```

### React Integration

The React integration method uses NPM packages and provides full component customization:

```jsx
import ReactWebChat, { createDirectLine } from 'botframework-webchat';

const directLine = createDirectLine({ token: 'YOUR_DIRECT_LINE_TOKEN' });
return <ReactWebChat directLine={directLine} userID="YOUR_USER_ID" />;
```

### iframe Integration

The iframe integration method embeds Web Chat through a hosted service with URL parameters for configuration.

Sources: [README.md:172-257]()

## Common Configuration Options

All integration methods support core configuration options for authentication, user identification, and basic styling:

| Configuration | Description | JavaScript | React | iframe |
|--------------|-------------|------------|-------|--------|
| `directLine` | DirectLine connection object | ✓ | ✓ | via URL params |
| `userID` | User identifier | ✓ | ✓ | via URL params |
| `username` | Display name | ✓ | ✓ | via URL params |
| `locale` | Localization setting | ✓ | ✓ | via URL params |
| `styleOptions` | Styling configuration | ✓ | ✓ | limited |
| `store` | Redux store | ✓ | ✓ | ✗ |

Sources: [README.md:225-228]()

## Security Considerations

The Bot Framework Web Chat supports Content Security Policy (CSP) and follows security best practices. Token-based authentication is strongly recommended over direct secret usage in client applications.

Key security recommendations:
- Use token-based authentication instead of embedding secrets
- Implement proper token refresh mechanisms
- Enable CSP headers for additional security
- Validate user inputs and sanitize content

For detailed security information, see the Content Security Policy documentation referenced in the repository.

Sources: [README.md:14](), [README.md:164]()

---

