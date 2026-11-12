<!-- source: DeepWiki mcp.deepwiki.com · repo openai/sign-in-with-chatgpt-devkit · page 7 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/security.md](docs/security.md)
- [examples/component-gallery/src/Gallery.tsx](examples/component-gallery/src/Gallery.tsx)
- [examples/component-gallery/src/gallery.css](examples/component-gallery/src/gallery.css)
- [examples/paste-perfect/electron/main.ts](examples/paste-perfect/electron/main.ts)
- [packages/local/src/types.ts](packages/local/src/types.ts)

</details>



This page provides definitions for terms specific to the Sign in with ChatGPT DevKit, including code pointers to their implementation, data flow, and key functions or classes.

## SIWC

**SIWC** is an acronym for "Sign in with ChatGPT". It refers to the authentication and authorization system that allows users to sign in to applications using their ChatGPT account. The DevKit provides tools and components to integrate SIWC into local Node.js applications and React UIs.

Sources: [README.md:1-3]()

## @siwc/local

`@siwc/local` is the local Node.js SDK package within the DevKit monorepo. It handles core functionalities like OAuth, credential storage, account profiles, model discovery, and streaming responses from the ChatGPT API. It is designed to run in the trusted local Node.js process of an application.

Sources: [README.md:18](), [README.md:24]()

## @siwc/react

`@siwc/react` is the React component library package within the DevKit monorepo. It provides UI components for integrating Sign in with ChatGPT features into a React application, such as sign-in buttons, connection status cards, and usage indicators.

Sources: [README.md:18](), [README.md:25]()

## LoginProfile

A `LoginProfile` represents a user's saved ChatGPT account connection within the application. It includes information like a unique ID, a user-defined label, the connection status, whether plan sharing is enabled, and optional identity details (name, email). It does not contain sensitive credentials directly.

```typescript
export interface LoginProfile {
  id: string;
  label: string;
  status: SessionState["status"];
  sharing: boolean;
  identity?: SessionIdentity;
  /** A pre-migration localhost registration cannot change its registered callback host. */
  requiresNewRegistration?: boolean;
  /** Registration returned a client ID but identity validation has not completed yet. */
  pending?: boolean;
}
```

Sources: [packages/local/src/types.ts:26-36]()

## StoredState

`StoredState` is an internal persistence type used by the `@siwc/local` SDK to manage all saved connection information. It includes the currently active profile ID, a list of `StoredProfile` objects, and any `PendingRegistration` objects. This state is encrypted at rest using the `CredentialEncryption` provider.

```typescript
export interface StoredState {
  version: 2;
  activeProfileId?: string;
  profiles: StoredProfile[];
  pendingRegistrations: PendingRegistration[];
}
```

Sources: [packages/local/src/types.ts:149-154]()

## Sharing Scope

"Sharing scope" refers to whether a user has granted permission for their ChatGPT plan to be used by the application. When `sharing` is `true` in a `SessionState` or `LoginProfile`, it indicates that the user has consented to share their plan. This enables the application to make API requests using the user's plan.

Sources: [packages/local/src/types.ts:19](), [packages/local/src/types.ts:30]()

## PendingRefresh

`PendingRefresh` is an internal state within a `StoredConnection` that holds newly rotated credentials (access token, refresh token, ID token) after a token refresh operation. These credentials are encrypted and stored in a pending state until their associated ID token can be successfully verified. This mechanism ensures that credentials are not used before identity validation is complete, even across app restarts or temporary network outages.

```typescript
export interface PendingRefresh {
  credentials: StoredCredentials;
  scopes: string[];
  idToken: string;
  /** Trusted local receipt time; retries validate the ID token as received, not after an outage. */
  receivedAt: number;
}
```

Sources: [packages/local/src/types.ts:114-120](), [docs/security.md:10-11]()

## CredentialEncryption

`CredentialEncryption` is an interface that defines the contract for an application-supplied provider responsible for encrypting and decrypting sensitive credentials. The `@siwc/local` SDK requires an implementation of this interface to ensure that access tokens, refresh tokens, and ID tokens are never stored in plaintext. The Paste Perfect example uses Electron's `safeStorage` for this purpose.

```typescript
export interface CredentialEncryption {
  /** Stable format identifier. Keep this unchanged while existing files use this provider. */
  id: string;
  isAvailable(): boolean | Promise<boolean>;
  encrypt(plaintext: string): Uint8Array | Promise<Uint8Array>;
  decrypt(ciphertext: Uint8Array): string | Promise<string>;
}
```

Sources: [packages/local/src/types.ts:44-50](), [docs/security.md:5-7]()

## safeStorage

`safeStorage` is an Electron API that provides an OS-backed mechanism for encrypting and decrypting data. In the Paste Perfect example, `safeStorage` is used to implement the `CredentialEncryption` interface, leveraging macOS Keychain to protect the encryption key. This ensures that sensitive user credentials are securely stored at rest.

Sources: [docs/security.md:5](), [examples/paste-perfect/electron/main.ts:36]()

## PKCE

**PKCE** (Proof Key for Code Exchange) is an extension to the OAuth 2.0 authorization code flow designed to prevent authorization code interception attacks. The DevKit's OAuth implementation uses PKCE to secure the sign-in process, ensuring that the authorization code can only be exchanged for tokens by the legitimate client.

Sources: [docs/security.md:21]()

## OIDC nonce

An **OIDC nonce** is a cryptographically secure random string used in OpenID Connect (OIDC) flows to mitigate replay attacks. The DevKit's OAuth implementation includes an OIDC nonce during the authorization request, and this nonce is then validated against the `id_token` received from the identity provider to ensure the token's freshness and prevent its reuse.

Sources: [docs/security.md:21]()

## Responses API

The **Responses API** is the backend service that the `@siwc/local` SDK interacts with to stream responses from ChatGPT models. The `streamResponse` function in the `ChatGPTClient` interface is used to send input and receive streaming output from this API.

Sources: [packages/local/src/types.ts:103]()

## Recipe

In the context of the Paste Perfect example app, a **recipe** is a predefined set of instructions or a prompt that is sent to the ChatGPT model to transform copied text. Users can select from various recipes (e.g., Spreadsheet, Message, Translate) to apply different transformations to their clipboard content. Recipes are stored locally as JSON and are not covered by credential encryption.

Sources: [examples/paste-perfect/electron/main.ts:49](), [docs/security.md:25]()

## Arm Paste Menu

"Arm paste menu" refers to the action of preparing the native macOS helper application to display a context menu with ChatGPT transformation options. When the user triggers the global shortcut (e.g., ⌘⇧Space), the application "arms" the paste menu, making the transformation options available for a limited time when the user right-clicks in a compatible text field.

Sources: [examples/paste-perfect/electron/main.ts:155]()

## Command Authenticator

The **command authenticator** is a security mechanism used in the Paste Perfect app to ensure that commands sent from the Electron main process to the native macOS helper are legitimate. It's a random, per-launch token delivered only to the validated main process via stdin. This prevents unauthorized processes from sending commands to the native helper.

Sources: [docs/security.md:23]()

## ASAR Integrity

**ASAR integrity** refers to the verification process for the ASAR (Atom Shell Archive) archive used by Electron applications. In the Paste Perfect app, the Electron dashboard and its dependencies are packaged into an ASAR archive, and its integrity is checked to prevent tampering and ensure that only trusted code is executed.

Sources: [docs/security.md:23]()

## Specimen Kind

In the Component Gallery, `SpecimenKind` is a type that categorizes how a UI component example is presented. It can be `'source'` (representing the original design), `'adapted'` (showing how the design is adapted for integration), or `'implementation'` (demonstrating the actual code implementation state). This helps developers understand the design lineage and implementation status of each component.

```typescript
type SpecimenKind = 'source' | 'adapted' | 'implementation';
```

Sources: [examples/component-gallery/src/Gallery.tsx:25](), [examples/component-gallery/src/Gallery.tsx:40-45]()

## Limit Window

A **limit window** refers to a specific time period or usage boundary within which a user's ChatGPT plan usage is measured. The `ChatGPTUsageIndicator` and `ChatGPTUsageCallout` components can display information related to these limit windows, helping users understand their current usage against their plan limits.

Sources: [packages/react/src/types.ts:12]()

## Usage Source

A **usage source** indicates where the ChatGPT plan usage originates from. In the context of the DevKit, it helps to clarify which application or feature is consuming the user's ChatGPT plan. The `ChatGPTUsageIndicator` component can display this information.

Sources: [packages/react/src/types.ts:13]()

## Provenance

**Provenance** refers to the origin and history of assets, particularly fonts, within the DevKit. The `provenance.json` file contains hashes and other metadata to verify the integrity and licensing of bundled fonts like Inter and Open Sans.

Sources: [README.md:67]()

## OFL

**OFL** stands for the Open Font License. This is a free and open-source license under which fonts like Inter and Open Sans are distributed within the DevKit. The license terms are included with the bundled fonts.

Sources: [README.md:67]()

## Noncommercial License

The **Noncommercial License** refers to the specific license under which the OpenAI-authored code and documentation of the Sign in with ChatGPT DevKit are distributed. It is the "Sign-in with ChatGPT DevKit Noncommercial License v1.0", which restricts commercial use of the DevKit.

Sources: [README.md:65]()