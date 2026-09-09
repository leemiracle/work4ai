> 来源: [https://deepwiki.com/deepseek-ai/deepseek-harness/5-api-layer-and-host-client-bridge](https://deepwiki.com/deepseek-ai/deepseek-harness/5-api-layer-and-host-client-bridge)
> DeepWiki deepseek-ai/deepseek-harness

# API Layer & Host-Client Bridge

  Relevant source files 
 - [.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.i18n.yaml)
 - [.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.md?plain=1)
 - [.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-api-browser-trust-boundary.zh.md?plain=1)
 - [.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.i18n.yaml)
 - [.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.md?plain=1)
 - [.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/architecture/2026-07-28-portable-execution-world-consumers.zh.md?plain=1)
 - [packages/api/gateway/src/client/remote-events.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/client/remote-events.ts)
 - [packages/api/gateway/src/client/remote-stream.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/client/remote-stream.ts)
 - [packages/api/gateway/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts)
 - [packages/api/gateway/src/stream-protocol.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/stream-protocol.ts)
 - [packages/api/gateway/src/stream-server.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/stream-server.ts)
 - [packages/api/gateway/src/types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/types.ts)
 - [packages/api/gateway/tests/control-retry.client.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/control-retry.client.spec.ts)
 - [packages/api/gateway/tests/gateway-stream.host.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/gateway-stream.host.spec.ts)
 - [packages/api/gateway/tests/gateway.client.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/gateway.client.spec.ts)
 - [packages/api/gateway/tests/gateway.host.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/gateway.host.spec.ts)
 - [packages/api/gateway/tests/stream-server.host.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/stream-server.host.spec.ts)
 - [packages/api/remotes/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/remotes/src/index.ts)
 - [packages/client/connection/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/README.i18n.yaml)
 - [packages/client/connection/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/README.md?plain=1)
 - [packages/client/connection/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/README.zh.md?plain=1)
 - [packages/client/connection/src/api-request-trust.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/api-request-trust.ts)
 - [packages/client/connection/src/client/api.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/api.ts)
 - [packages/client/connection/src/client/connection.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/connection.ts)
 - [packages/client/connection/src/client/fixture.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/fixture.ts)
 - [packages/client/connection/src/client/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/index.ts)
 - [packages/client/connection/src/client/random-uuid.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/random-uuid.ts)
 - [packages/client/connection/src/client/rpc.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/rpc.ts)
 - [packages/client/connection/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/index.ts)
 - [packages/client/connection/src/rpc-host.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/rpc-host.ts)
 - [packages/client/connection/src/rpc.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/rpc.ts)
 - [packages/client/connection/tests/client-apply.client.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/tests/client-apply.client.spec.ts)
 - [packages/client/connection/tests/connection.client.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/tests/connection.client.spec.ts)
 - [packages/client/connection/tests/fetch-routes.host.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/tests/fetch-routes.host.spec.ts)
 - [packages/client/connection/tests/node-half.host.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/tests/node-half.host.spec.ts)
 - [packages/typert/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/typert/README.i18n.yaml)
 
  The **API Layer & Host-Client Bridge** provides the communication infrastructure between the Node.js host and the browser-based Web UI. It is designed to be transport-agnostic, type-safe, and capable of handling both unary RPC calls and complex event streaming.

 The system ensures that the client can interact with the host's plugin-based services (like the Agent loop, Filesystem, and Session Store) as if they were local, while maintaining strict validation and a browser-trust boundary.

 
### Architecture Overview

 The bridge consists of three primary components:

 
 - **API Proxy & RPC Protocol**: The wire protocol and gateway service that routes messages and enforces security.
 - **Typert**: A build-time tool that generates TypeScript declarations for remote services, ensuring type safety across the bridge.
 - **Client Runtime**: The browser-side implementation that manages session state, stream dispatching, and connection lifecycles.
 
 
#### System Entity Map: Host to Client

 The following diagram maps high-level system concepts to the specific code entities that implement them.

 
```

```

 **Sources:** [packages/client/connection/src/index.ts108-112](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/index.ts#L108-L112) [packages/api/gateway/src/index.ts173-208](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L173-L208) [packages/client/connection/src/client/index.ts105-131](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/index.ts#L105-L131)

 
---

 
## 5.1 API Proxy & RPC Protocol

 The `client-connection` package and `TypertGateway` form the central gateway on the host. It exposes methods for session management, workspace organization, and host-level operations.

 
 - **Wire Protocol**: Uses a structured RPC format: `ClientRequest` (POST body), `ServerResponse` (POST response), and `RpcMessage` for streaming [packages/client/connection/src/rpc.ts1-50](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/rpc.ts#L1-L50)
 - **Validation**: Every message is validated using Zod/Schemastery schemas (e.g., `clientRequestSchema`, `rpcMessageSchema`) [packages/client/connection/src/rpc-schema.ts35-41](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/rpc-schema.ts#L35-L41)
 - **Security**: Implements a browser-trust fence. The `BrowserAuth` service manages signed, authority-bound cookies, while `assertTrustedAuthority` prevents DNS rebinding by checking `Host` and `Origin` headers [packages/client/connection/src/browser-auth.ts1-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/browser-auth.ts#L1-L20) [packages/client/connection/src/api-request-trust.ts1-15](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/api-request-trust.ts#L1-L15)
 - **Streaming**: The `TypertGatewayService` manages `RemoteStreamMuxServer`, which handles multiplexed WebSocket connections for real-time events and streaming tool outputs [packages/api/gateway/src/stream-server.ts1-40](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/stream-server.ts#L1-L40)
 
 For details, see [API Proxy & RPC Protocol](https://deepwiki.com/deepseek-ai/deepseek-harness/5.1-api-proxy-and-rpc-protocol).

 **Sources:** [packages/client/connection/src/index.ts99-131](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/index.ts#L99-L131) [packages/client/connection/README.md32-40](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/README.md?plain=1#L32-L40) [packages/api/gateway/src/index.ts173-210](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L173-L210)

 
---

 
## 5.2 Typert: Type-Safe RPC Generation

 `Typert` is the framework for generating "Host-for-Client" remote declarations. It allows host services to be decorated and automatically exposed to the client with full type fidelity.

 
 - **Decorators**: Uses `@Remote` (with `mode: 'stream'` or unary) to mark Cordis services and methods reachable over the bridge [packages/api/gateway/tests/gateway-stream.host.spec.ts73-87](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/gateway-stream.host.spec.ts#L73-L87)
 - **Registry**: `TypertRegistry` maintains the mapping of available remote endpoints, which `TypertGatewayService` uses to route incoming requests to the correct service instance [packages/api/gateway/src/index.ts174-188](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L174-L188)
 - **Protocol**: Defines the `InvocationDescriptor` and `TypertCodec` to ensure arguments and return values are serialized correctly across the wire [packages/api/gateway/src/index.ts15-32](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L15-L32)
 
 For details, see [Typert: Type-Safe RPC Generation](https://deepwiki.com/deepseek-ai/deepseek-harness/5.2-typert:-type-safe-rpc-generation).

 **Sources:** [packages/api/gateway/src/index.ts173-208](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L173-L208) [packages/api/gateway/tests/gateway-stream.host.spec.ts64-136](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/tests/gateway-stream.host.spec.ts#L64-L136) [packages/typert/README.md1-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/typert/README.md?plain=1#L1-L20)

 
---

 
## 5.3 Client Runtime & Session Management

 The Client Runtime translates raw RPC and multiplexed streams into a coherent state for the UI.

 
 - **Connection Management**: The `ConnectionController` manages the connect/reconnect loop, handling backoff and "generation" resets when the physical transport (WebSocket) drops [packages/client/connection/src/client/connection.ts1-100](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/connection.ts#L1-L100)
 - **SessionRuntime**: Manages the lifecycle of a single session, subscribing to event streams and handling history paging.
 - **Event Folding**: Logic like `foldSurface` and `deriveEventMessage` take raw `SessionEvent` sequences and project them into the message tree for rendering [packages/client/connection/src/client/fixture.ts35](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/fixture.ts#L35-L35)
 - **Fixture Mode**: A standalone `fixture.ts` provides a mock implementation of the entire Host API, allowing UI development and testing without a running Node.js backend [packages/client/connection/src/client/fixture.ts1-40](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/fixture.ts#L1-L40)
 
 For details, see [Client Runtime & Session Management](https://deepwiki.com/deepseek-ai/deepseek-harness/5.3-client-runtime-and-session-management).

 **Sources:** [packages/client/connection/src/client/index.ts143-182](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/index.ts#L143-L182) [packages/client/connection/src/client/fixture.ts1-236](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/client/fixture.ts#L1-L236) [packages/client/connection/README.md41-47](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/README.md?plain=1#L41-L47)

 
---

 
### Communication Flow Diagram

 This diagram illustrates how a client-side call travels to the host and how events stream back.

 
```

```

 **Sources:** [packages/client/connection/src/index.ts113-127](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/index.ts#L113-L127) [packages/api/gateway/src/index.ts202-208](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/api/gateway/src/index.ts#L202-L208) [packages/client/connection/src/rpc.ts1-50](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/client/connection/src/rpc.ts#L1-L50)
