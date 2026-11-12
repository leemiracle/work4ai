<!-- source: DeepWiki mcp.deepwiki.com · repo android/codelab-fido2 · page 1 WebAuthn Codelab Overview · fetched 2026-10-23 -->

# WebAuthn Codelab Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/auth.js](libs/auth.js)
- [package.json](package.json)
- [public/client.js](public/client.js)
- [server.js](server.js)

</details>



## Purpose and Scope

This document provides an architectural overview of the WebAuthn Codelab, a comprehensive educational repository that demonstrates FIDO2/WebAuthn authentication across three platforms: web client, web server, and Android application. The codelab implements passwordless authentication using platform authenticators and cross-platform credential sharing.

For detailed implementation of specific components, see [Web Application](#2) for browser and server implementations, [Android Application](#3) for mobile client details, and [WebAuthn and FIDO2 Implementation](#4) for authentication protocol specifics.

## System Architecture

The WebAuthn Codelab consists of three interconnected systems that demonstrate modern passwordless authentication:

### Three-Platform Authentication System

```mermaid
graph TB
    subgraph "Web_Client" ["Web Client Platform"]
        WC_HTML["index.html, reauth.html, home.html"]
        WC_JS["client.js"]
        WC_API["navigator.credentials WebAuthn API"]
    end
    
    subgraph "Web_Server" ["Express.js Server"]
        SERVER_MAIN["server.js"]
        AUTH_ROUTER["libs/auth.js"]
        LOWDB_STORAGE[".data/db.json lowdb storage"]
        SIMPLEWEBAUTHN["@simplewebauthn/server"]
    end
    
    subgraph "Android_Platform" ["Android Application"]
        ANDROID_APP["FIDO2 Android App"]
        PLAY_SERVICES["Google Play Services FIDO2"]
        ASSETLINKS["/.well-known/assetlinks.json"]
    end
    
    WC_JS --> |"HTTP POST /auth/*"| AUTH_ROUTER
    WC_API --> |"WebAuthn credentials.create()/get()"| WC_JS
    
    SERVER_MAIN --> AUTH_ROUTER
    AUTH_ROUTER --> LOWDB_STORAGE
    AUTH_ROUTER --> SIMPLEWEBAUTHN
    SERVER_MAIN --> ASSETLINKS
    
    ANDROID_APP --> |"HTTP okhttp User-Agent"| AUTH_ROUTER
    ANDROID_APP --> PLAY_SERVICES
    ASSETLINKS --> |"Digital Asset Links"| ANDROID_APP
    
    WC_HTML --> WC_JS
```

Sources: [server.js:1-128](), [libs/auth.js:1-483](), [public/client.js:1-162](), [package.json:1-45]()

### Core Authentication Flow

The system implements a complete WebAuthn authentication cycle with credential registration, authentication, and management:

#### Registration and Authentication Endpoints

```mermaid
sequenceDiagram
    participant CLIENT as "Client (Web/Android)"
    participant EXPRESS as "server.js Express App"
    participant AUTH as "libs/auth.js Router"
    participant LOWDB as "lowdb .data/db.json"
    participant SIMPLEWEBAUTHN as "@simplewebauthn/server"
    
    Note over CLIENT,SIMPLEWEBAUTHN: Registration Flow
    CLIENT->>AUTH: "POST /auth/registerRequest"
    AUTH->>SIMPLEWEBAUTHN: "generateAttestationOptions()"
    SIMPLEWEBAUTHN-->>AUTH: "PublicKeyCredentialCreationOptions"
    AUTH-->>CLIENT: "challenge, excludeCredentials, rp info"
    
    CLIENT->>CLIENT: "navigator.credentials.create() or FIDO2 API"
    CLIENT->>AUTH: "POST /auth/registerResponse + credential"
    AUTH->>SIMPLEWEBAUTHN: "verifyAttestationResponse()"
    AUTH->>LOWDB: "Store user.credentials[]"
    
    Note over CLIENT,SIMPLEWEBAUTHN: Authentication Flow  
    CLIENT->>AUTH: "POST /auth/signinRequest"
    AUTH->>SIMPLEWEBAUTHN: "generateAssertionOptions()"
    AUTH-->>CLIENT: "challenge, allowCredentials"
    
    CLIENT->>CLIENT: "navigator.credentials.get() or FIDO2 API"
    CLIENT->>AUTH: "POST /auth/signinResponse + assertion"
    AUTH->>SIMPLEWEBAUTHN: "verifyAssertionResponse()"
    AUTH->>LOWDB: "Update prevCounter"
```

Sources: [libs/auth.js:186-291](), [libs/auth.js:308-361](), [libs/auth.js:377-422](), [libs/auth.js:439-480]()

## Platform-Specific Implementations

### Web Client Implementation

The web client uses standard WebAuthn APIs with base64url encoding utilities and HTTP communication:

| Component | File | Key Functions |
|-----------|------|---------------|
| WebAuthn Integration | `client.js` | `registerCredential()`, `authenticate()` |
| Base64URL Utilities | `client.js` | `base64url.encode()`, `base64url.decode()` |
| HTTP Communication | `client.js` | `_fetch()` utility |
| UI Templates | `views/*.html` | Login, reauth, credential management |

The client implementation handles WebAuthn credential creation and authentication through browser APIs:

```mermaid
flowchart TD
    REGISTER_CRED["registerCredential()"]
    AUTH_CRED["authenticate()"]
    UNREG_CRED["unregisterCredential()"]
    
    REGISTER_CRED --> FETCH_REQ["/auth/registerRequest"]
    FETCH_REQ --> DECODE_OPTS["base64url.decode() options"]
    DECODE_OPTS --> NAV_CREATE["navigator.credentials.create()"]
    NAV_CREATE --> ENCODE_RESP["base64url.encode() response"]
    ENCODE_RESP --> FETCH_RESP["/auth/registerResponse"]
    
    AUTH_CRED --> SIGNIN_REQ["/auth/signinRequest"]
    SIGNIN_REQ --> DECODE_CHALLENGE["base64url.decode() challenge"]
    DECODE_CHALLENGE --> NAV_GET["navigator.credentials.get()"]
    NAV_GET --> ENCODE_ASSERTION["base64url.encode() assertion"]
    ENCODE_ASSERTION --> SIGNIN_RESP["/auth/signinResponse"]
    
    UNREG_CRED --> REMOVE_KEY["/auth/removeKey"]
    REMOVE_KEY --> LOCALSTORAGE_CLEAR["localStorage.removeItem()"]
```

Sources: [public/client.js:62-105](), [public/client.js:107-156](), [public/client.js:158-161]()

### Server Architecture

The Express.js server provides WebAuthn endpoints, session management, and cross-platform origin handling:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `server.js` | Main application, routing, session config | Express app with `express-session` |
| `libs/auth.js` | Authentication router and WebAuthn logic | SimpleWebAuthn integration |
| `lowdb` storage | User and credential persistence | JSON file database |
| Asset links | Android app verification | Digital Asset Links endpoint |

The server handles both web and Android clients through origin detection:

```mermaid
graph TB
    EXPRESS_APP["server.js Express Application"]
    
    subgraph "Route_Handlers" ["HTTP Route Handlers"]
        ROOT_ROUTE["GET / → index.html or redirect"]
        HOME_ROUTE["GET /home → home.html"]
        REAUTH_ROUTE["GET /reauth → reauth.html"]
        ASSETLINKS["GET /.well-known/assetlinks.json"]
    end
    
    subgraph "Auth_Router" ["libs/auth.js Authentication Router"]
        USERNAME_POST["POST /auth/username"]
        PASSWORD_POST["POST /auth/password"]
        REGISTER_REQ["POST /auth/registerRequest"]
        REGISTER_RESP["POST /auth/registerResponse"]
        SIGNIN_REQ["POST /auth/signinRequest"]
        SIGNIN_RESP["POST /auth/signinResponse"]
        GET_KEYS["POST /auth/getKeys"]
        REMOVE_KEY["POST /auth/removeKey"]
    end
    
    subgraph "Session_Management" ["Express Session & CSRF"]
        SESSION_CHECK["sessionCheck() middleware"]
        CSRF_CHECK["csrfCheck() middleware"]
        EXPRESS_SESSION["express-session storage"]
    end
    
    subgraph "Data_Layer" ["Data Persistence"]
        LOWDB_USERS["lowdb users[] array"]
        USER_CREDENTIALS["user.credentials[] storage"]
    end
    
    subgraph "WebAuthn_Integration" ["SimpleWebAuthn Library"]
        GENERATE_ATTESTATION["generateAttestationOptions()"]
        VERIFY_ATTESTATION["verifyAttestationResponse()"]
        GENERATE_ASSERTION["generateAssertionOptions()"]
        VERIFY_ASSERTION["verifyAssertionResponse()"]
    end
    
    EXPRESS_APP --> Route_Handlers
    EXPRESS_APP --> Auth_Router
    
    Auth_Router --> Session_Management
    Auth_Router --> Data_Layer
    Auth_Router --> WebAuthn_Integration
    
    ASSETLINKS --> |"Android package verification"| Auth_Router
```

Sources: [server.js:18-128](), [libs/auth.js:17-48](), [libs/auth.js:266-277](), [libs/auth.js:406-415]()

## Cross-Platform Origin Handling

The server supports both web and Android clients through dynamic origin detection:

```mermaid
flowchart LR
    USER_AGENT["req.get('User-Agent')"]
    
    USER_AGENT --> WEB_CHECK{"userAgent.indexOf('okhttp') === 0"}
    
    WEB_CHECK -->|"false"| WEB_ORIGIN["process.env.ORIGIN\n(https://domain)"]
    WEB_CHECK -->|"true"| ANDROID_CALC["Calculate Android APK hash origin"]
    
    ANDROID_CALC --> ANDROID_ORIGIN["android:apk-key-hash:${androidHash}"]
    
    WEB_ORIGIN --> WEBAUTHN_VERIFY["WebAuthn Origin Verification"]
    ANDROID_ORIGIN --> WEBAUTHN_VERIFY
```

Sources: [libs/auth.js:62-74](), [server.js:95-119]()

## Database Schema and Storage

The codelab uses `lowdb` for simple JSON-based storage with the following structure:

| Entity | Schema | Purpose |
|--------|--------|---------|
| `users[]` | Array of user objects | Main user storage |
| `user.username` | String | User identifier |
| `user.id` | Base64URL string | WebAuthn user ID |
| `user.credentials[]` | Array of credential objects | Stored authenticators |
| `credential.credId` | Base64URL string | Credential identifier |
| `credential.publicKey` | Base64URL string | Public key for verification |
| `credential.prevCounter` | Integer | Signature counter |

Sources: [libs/auth.js:25-41](), [libs/auth.js:88-103](), [libs/auth.js:341-349]()

## Technology Stack

The codelab demonstrates WebAuthn across multiple technology stacks:

### Dependencies and Build System

| Platform | Core Dependencies | Purpose |
|----------|-------------------|---------|
| Web Server | `express`, `express-session`, `@simplewebauthn/server`, `lowdb` | HTTP server and WebAuthn |
| Web Client | `@material/mwc-*` components, `webpack`, `babel` | UI and build tooling |
| Android | Google Play Services FIDO2 API | Platform authentication |

Sources: [package.json:10-31]()

This codelab provides a complete educational foundation for implementing WebAuthn authentication across web and mobile platforms, with shared credential storage and cross-platform compatibility.

---

