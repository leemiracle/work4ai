<!-- source: DeepWiki mcp.deepwiki.com · repo openai/sign-in-with-chatgpt-devkit · page 2 @siwc/local — Local Node SDK · fetched 2026-10-26 -->

# @siwc/local — Local Node SDK

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/local/package.json](packages/local/package.json)
- [packages/local/src/index.ts](packages/local/src/index.ts)
- [packages/local/src/types.ts](packages/local/src/types.ts)

</details>



The `@siwc/local` package provides a Node.js SDK for integrating Sign in with ChatGPT functionality into local applications. It manages the entire lifecycle of ChatGPT connections, including authentication, credential storage, session management, and interaction with the ChatGPT API. This package is designed to be run in a trusted local process, such as an Electron main process, and exposes a safe API for application-level interactions.

The core of this SDK is the `createChatGPT` function, which initializes a `ChatGPTClient` instance. This client handles secure credential management, OAuth flows, and communication with the ChatGPT services. It abstracts away the complexities of token refresh, identity verification, and error handling, providing a streamlined interface for developers.

Sources:
- [packages/local/package.json:2-32]()
- [packages/local/src/index.ts:66-72]()
- [packages/local/src/types.ts:93-104]()

## Core Components

The `@siwc/local` SDK is structured around several key components and concepts:

### `ChatGPTClient`

The `ChatGPTClient` is the primary interface for interacting with the SDK. It is created using the `createChatGPT` function and provides methods for signing in, managing profiles, listing models, and streaming responses. The client maintains the session state and ensures secure handling of credentials.

Sources:
- [packages/local/src/index.ts:66-72]()
- [packages/local/src/types.ts:93-104]()

### Session and Profile Management

The SDK manages user sessions and profiles, allowing applications to support multiple ChatGPT connections. A `SessionState` object represents the current status of the active connection, while `LoginProfile` objects provide details about all available connections. The SDK handles the selection, disconnection, and reauthentication of profiles.

Sources:
- [packages/local/src/index.ts:19-42]()
- [packages/local/src/types.ts:17-36]()

### Credential Storage and Encryption

Secure storage of credentials is a critical aspect of the SDK. It uses a `ConnectionStore` to persist connection data and requires a `CredentialEncryption` provider to encrypt and decrypt sensitive information. This ensures that access tokens and refresh tokens are never stored in plaintext. For details, see [Credential Storage and Encryption](#2.2).

Sources:
- [packages/local/src/index.ts:72-72]()
- [packages/local/src/types.ts:43-50]()

### OAuth and Sign-In Flow

The SDK implements the OAuth 2.0 authorization code flow with PKCE and OIDC nonce for secure authentication. It handles the entire sign-in process, including opening the browser for user authorization, receiving callbacks, and exchanging authorization codes for tokens. It also manages token refresh, identity verification, and revocation. For details, see [OAuth and Sign-In Flow](#2.1).

Sources:
- [packages/local/src/index.ts:6-6]()
- [packages/local/src/types.ts:83-91]()

### Model Discovery and Streaming Responses

The SDK provides functionality to discover available ChatGPT models and to stream responses from the ChatGPT API. It abstracts the API interaction, allowing applications to easily integrate conversational AI capabilities. For details, see [Models and Streaming Responses](#2.3).

Sources:
- [packages/local/src/index.ts:5-5]()
- [packages/local/src/index.ts:7-7]()
- [packages/local/src/types.ts:38-41]()
- [packages/local/src/types.ts:75-81]()

### Error Handling

The SDK defines a comprehensive error model using `ChatGPTError` to provide detailed information about issues that may arise during operation. Errors are categorized and include properties like `code`, `message`, and `retryable`, helping applications to implement robust error handling strategies. For details, see [Error Model and Types](#2.4).

Sources:
- [packages/local/src/index.ts:4-4]()
- [packages/local/src/types.ts:6-14]()

## Architecture Diagram: `ChatGPTClient` and its Dependencies

```mermaid
graph TD
    subgraph "Application Process (e.g., Electron Main)"
        A["Your Application Code"] --> B(createChatGPT(config))
        B --> C(ChatGPTClient)
    end

    subgraph "@siwc/local SDK"
        C -- "Manages Session State" --> D(SessionState)
        C -- "Manages Login Profiles" --> E(LoginProfile)
        C -- "Handles OAuth Flow" --> F(oauth.ts)
        C -- "Stores Credentials" --> G(ConnectionStore)
        C -- "Encrypts/Decrypts Credentials" --> H(CredentialEncryption)
        C -- "Interacts with ChatGPT API" --> I(models.ts)
        C -- "Interacts with ChatGPT API" --> J(responses.ts)
        C -- "Provides Error Model" --> K(errors.ts)
    end

    subgraph "External Services"
        F -- "Browser for User Auth" --> L(ChatGPT Auth Server)
        I -- "API Calls" --> M(ChatGPT API)
        J -- "API Calls" --> M
    end

    style A fill:#ace,stroke:#333,stroke-width:2px
    style B fill:#bcf,stroke:#333,stroke-width:2px
    style C fill:#bcf,stroke:#333,stroke-width:2px
    style D fill:#def,stroke:#333,stroke-width:1px
    style E fill:#def,stroke:#333,stroke-width:1px
    style F fill:#def,stroke:#333,stroke-width:1px
    style G fill:#def,stroke:#333,stroke-width:1px
    style H fill:#def,stroke:#333,stroke-width:1px
    style I fill:#def,stroke:#333,stroke-width:1px
    style J fill:#def,stroke:#333,stroke-width:1px
    style K fill:#def,stroke:#333,stroke-width:1px
    style L fill:#fcc,stroke:#333,stroke-width:1px
    style M fill:#fcc,stroke:#333,stroke-width:1px
```
Title: "ChatGPTClient" and its Dependencies
Sources:
- [packages/local/src/index.ts:66-72]()
- [packages/local/src/types.ts:93-104]()
- [packages/local/src/index.ts:4-8]()

## Data Flow: Session State and Profile Management

```mermaid
graph TD
    subgraph "Application Lifecycle"
        A[App Startup] --> B{createChatGPT(config)}
        B --> C[ChatGPTClient Instance]
    end

    subgraph "User Interaction"
        D[User Action: Sign In] --> C
        D[User Action: Select Profile] --> C
        D[User Action: Disconnect] --> C
    end

    subgraph "Internal SDK Logic"
        C -- "Calls signIn()" --> E(oauth.authorize)
        C -- "Calls selectProfile()" --> F(ConnectionStore.withLock)
        C -- "Calls disconnect()" --> G(revokeConnection)
        F -- "Reads/Writes" --> H(StoredState)
        H -- "Contains" --> I(StoredProfile[])
        H -- "Contains" --> J(PendingRegistration[])
        I -- "Maps to" --> K(LoginProfile[])
        H -- "Derives" --> L(SessionState)
    end

    subgraph "External Interactions"
        E -- "Redirects to" --> M(ChatGPT Auth Server)
        G -- "Revokes Token at" --> M
    end

    C -- "Publishes Updates" --> N[SessionState Subscribers]

    style A fill:#ace,stroke:#333,stroke-width:2px
    style B fill:#bcf,stroke:#333,stroke-width:2px
    style C fill:#bcf,stroke:#333,stroke-width:2px
    style D fill:#ace,stroke:#333,stroke-width:2px
    style E fill:#def,stroke:#333,stroke-width:1px
    style F fill:#def,stroke:#333,stroke-width:1px
    style G fill:#def,stroke:#333,stroke-width:1px
    style H fill:#def,stroke:#333,stroke-width:1px
    style I fill:#def,stroke:#333,stroke-width:1px
    style J fill:#def,stroke:#333,stroke-width:1px
    style K fill:#def,stroke:#333,stroke-width:1px
    style L fill:#def,stroke:#333,stroke-width:1px
    style M fill:#fcc,stroke:#333,stroke-width:1px
    style N fill:#ace,stroke:#333,stroke-width:2px
```
Title: Session State and Profile Management Data Flow
Sources:
- [packages/local/src/index.ts:19-42]()
- [packages/local/src/index.ts:73-86]()
- [packages/local/src/index.ts:108-110]()
- [packages/local/src/types.ts:17-36]()
- [packages/local/src/types.ts:149-154]()

## Child Pages

This parent page provides a high-level overview. For detailed information on specific aspects of the `@siwc/local` SDK, please refer to the following child pages:

*   **[OAuth and Sign-In Flow](#2.1)**: Delves into the specifics of the loopback OAuth implementation, PKCE, OIDC nonce, token refresh mechanisms, identity verification, and how to handle revocation, disconnection, reconsent, and profile selection.
*   **[Credential Storage and Encryption](#2.2)**: Explains the `ConnectionStore` for persistent data, the `CredentialEncryption` provider contract, atomic write operations, handling of pending refresh states, and the migration path for legacy plaintext credentials.
*   **[Models and Streaming Responses](#2.3)**: Covers how to discover available ChatGPT models using `listModels` and the `streamResponse` pipeline for interacting with the Responses API, including how usage and limit metadata are surfaced to the UI.
*   **[Error Model and Types](#2.4)**: Details the `ChatGPTError` codes, distinguishes between retryable and reauthentication errors, and outlines the exported TypeScript types and build configurations for robust error handling.

---

