<!-- source: DeepWiki mcp.deepwiki.com · repo agentgateway/agentgateway · page 11 Network and Transport · fetched 2026-10-21 -->

# Network and Transport

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [crates/agentgateway/src/transport/stream.rs](crates/agentgateway/src/transport/stream.rs)

</details>



This page describes the network protocols, transport layer abstractions, and connection management in the agentgateway data plane. It provides a high-level overview of how raw network streams are accepted via the `Socket` abstraction [crates/agentgateway/src/transport/stream.rs:116-120](), wrapped with protocol extensions or security layers, multiplexed through connection pools, and routed to backends.

For deep technical details, see the child pages:
- [Protocol Support Overview](#11.1) — Supported protocols: HTTP/1.1, HTTP/2, TCP, TLS, gRPC, WebSocket. Overview of the `Socket` abstraction and protocol detection mechanism.
- [TLS and mTLS Configuration](#11.2) — TLS termination, client certificates, mTLS validation, certificate authorities, and crypto provider options. Covers `tls.rs`, `backendtls.rs`, and the CA client.
- [HBONE Protocol (Istio Integration)](#11.3) — HBONE tunnel protocol, waypoint integration, and double-HBONE for service mesh. Covers `terminate_waypoint_hbone`, `serve_waypoint_connect`, and `HboneAddress`.
- [PROXY Protocol and Tunnels](#11.4) — PROXY protocol v2, identity extraction via TLV, HTTP CONNECT tunneling, and egress proxy support. Covers `terminate_proxy_protocol` and `connect_tunnel.rs`.
- [Connection Pooling and Management](#11.5) — Connection pooling, keep-alive, and resource cleanup. Covers the `pool` crate, HBONE pool, and MCP relay pool.
- [Substrate Ingress and Egress](#11.6) — Substrate agent-network integration: ingress/egress handling, ATE attributes and `ateapi.proto`, egress actor resolution, and semconv attributes. Covers `http/substrate/`.

---

## Transport Layer Architecture

The transport layer provides a polymorphic abstraction over raw network connections, bridging the OS socket level and the higher-layer proxy logic. The central `Socket` type abstracts underlying transport streams such as TCP, TLS-encrypted TCP, HBONE tunnels, and in-memory duplex streams [crates/agentgateway/src/transport/stream.rs:116-120](). It carries metadata extensions like `TCPConnectionInfo` (remote/local addresses and start time) [crates/agentgateway/src/transport/stream.rs:27-35]() and TLS state (`TLSConnectionInfo` including ALPN negotiation and client identities) [crates/agentgateway/src/transport/stream.rs:57-61]().

The gateway instantiates TCP listeners and drives connection acceptance that feeds into the protocol detection subsystem, responsible for dynamically identifying and dispatching appropriate protocols (e.g., plain HTTP, TLS, PROXY protocol, HBONE) for each connection. Upstream clients build on this foundation and use connector abstractions to establish outbound transports with TLS or specialized HBONE tunnels as needed.

```mermaid
title Transport Layer Component Relationships

graph TD
    Proxy["HTTPProxy"] -->|"Client::call"| UpstreamClient["client::Client"]
    UpstreamClient -->|"Pool lookup"| AgentPool["agent_pool::Client"]
    AgentPool -->|"Miss: connect()"| Connector["client::Connector"]
    Connector -->|"Transport::Plain"| DialTCP["client::dial"]
    Connector -->|"Transport::Hbone"| HboneConnect["client::hbone_tunnel::handshake"]
    Connector -->|"ApplicationTransport::Tls"| TLSWrap["Socket::from_tls"]
    
    Gateway["proxy::gateway::Gateway"] -->|"run_bind"| Accept["TcpListener"]
    Accept -->|"proxy_bind"| Detect["Protocol Detection"]
```

Sources: [crates/agentgateway/src/transport/stream.rs:27-35](), [crates/agentgateway/src/transport/stream.rs:57-61](), [crates/agentgateway/src/transport/stream.rs:116-120]()

---

## 11.1 Protocol Support Overview

The agentgateway supports multiple network protocols to serve diverse connection scenarios. Downstream protocols include HTTP/1.1, HTTP/2, TCP, TLS (including mutual TLS), gRPC, and WebSocket. Incoming connections are represented by the `Socket` abstraction [crates/agentgateway/src/transport/stream.rs:116-120](), which embeds metadata such as `TCPConnectionInfo` containing peer and local addresses [crates/agentgateway/src/transport/stream.rs:27-35]() as well as metrics counters for traffic measurement [crates/agentgateway/src/transport/stream.rs:75-80](). The `Alpn` enum [crates/agentgateway/src/transport/stream.rs:38-42]() is used to represent negotiated ALPN protocols like `Http11` and `H2`.

Protocol detection inspects connection prefaces and TLS handshakes where applicable to route processing to appropriate handlers. This includes detecting whether a connection is plain TCP, HTTP over TLS, HBONE tunneled, or using the PROXY protocol. The detection step is essential to seamlessly handle heterogeneous traffic within a single bind listener.

For details, see [Protocol Support Overview](#11.1).

Sources: [crates/agentgateway/src/transport/stream.rs:27-35](), [crates/agentgateway/src/transport/stream.rs:38-42](), [crates/agentgateway/src/transport/stream.rs:75-80](), [crates/agentgateway/src/transport/stream.rs:116-120]()

---

## 11.2 TLS and mTLS Configuration

TLS security is integral for encrypted transport and strong workload identity assertions. The project uses `rustls` to terminate TLS connections on listener binds. Configuration includes downstream TLS with certificate catalogs, client certificate validation for mutual TLS (mTLS), and upstream TLS for backend communication.

The `TLSConnectionInfo` structure [crates/agentgateway/src/transport/stream.rs:57-61]() records client identities extracted from TLS sessions, negotiated ALPN protocols (`Alpn::H2` or `Alpn::Http11`) [crates/agentgateway/src/transport/stream.rs:38-54](), and the requested server name (SNI). Nested TLS handling ensures multi-hop TLS (e.g., HBONE tunnels carrying TLS) preserves identity information without overwriting authenticated states [crates/agentgateway/src/transport/stream.rs:216-256]().

Certificate management supports dynamic rotation via integration with Istio's Citadel CA client. Upstream client TLS leverages these settings for connection dialing with options for custom CA bundles, SNI overrides, and protocol negotiation.

For details, see [TLS and mTLS Configuration](#11.2).

Sources: [crates/agentgateway/src/transport/stream.rs:38-54](), [crates/agentgateway/src/transport/stream.rs:57-61](), [crates/agentgateway/src/transport/stream.rs:216-256]()

---

## 11.3 HBONE Protocol (Istio Integration)

The HBONE (HTTP-Based Overlay Network) protocol is a tunnel mechanism designed for integrating service mesh environments such as Istio. The gateway supports terminating inbound HBONE tunnels, enabling waypoint proxy scenarios where traffic enters the mesh at designated nodes.

`HBONEConnectionInfo` captures the HBONE remote address for these tunnels [crates/agentgateway/src/transport/stream.rs:63-66](). The system supports nested HBONE tunnels (double-HBONE) for mesh-to-mesh forwarding and integrates with Istio waypoint conventions to manage egress/ingress securely.

This protocol abstraction facilitates advanced mesh networking layers while exposing a consistent transport interface to the proxy and connection pool components.

For details, see [HBONE Protocol (Istio Integration)](#11.3).

Sources: [crates/agentgateway/src/transport/stream.rs:63-66]()

---

## 11.4 PROXY Protocol and Tunnels

To maintain original client connection metadata behind load balancers or proxies, the agentgateway implements the PROXY protocol version 2 parsing. This preserves the original peer IP/port information in `TCPConnectionInfo.raw_peer_addr` [crates/agentgateway/src/transport/stream.rs:31-35](). Identity information encoded in TLV (Type-Length-Value) extensions within PROXY protocol headers allows the system to extract upstream identities reliably.

In addition to direct connections, the gateway supports HTTP CONNECT tunneling for encrypted TCP stream forwarding and manages egress proxy usage scenarios for outbound traffic. This functionality is crucial in complex network topologies requiring identity preservation and tunnel multiplexing.

For details, see [PROXY Protocol and Tunnels](#11.4).

Sources: [crates/agentgateway/src/transport/stream.rs:31-35]()

---

## 11.5 Connection Pooling and Management

The connection pooling subsystem is responsible for efficient reuse of upstream connections to backends, minimizing latency and resource consumption. The `Socket` type implements connection lifecycle traits such as `ConnectionDeadline` [crates/agentgateway/src/transport/stream.rs:133-134]() to signal when a connection should no longer be reused and `HttpProxy` [crates/agentgateway/src/transport/stream.rs:129-130]() to indicate HTTP proxying context.

Pooling logic manages keep-alive windows, idle connection cleanup, and TLS session reuse across pools specialized per transport type (plain TCP, TLS, HBONE tunnels, MCP relays). Metrics integration is used to observe pool health and performance. The pooling crates coordinate with the transport layer to instantiate and track connection states seamlessly.

For details, see [Connection Pooling and Management](#11.5).

Sources: [crates/agentgateway/src/transport/stream.rs:129-130](), [crates/agentgateway/src/transport/stream.rs:133-134]()

---

## 11.6 Substrate Ingress and Egress

The substrate integration layer handles ingress and egress of network flows within the agent-network context. It maps Agent Telemetry Events (ATE) attributes (`ateapi.proto`) to internal telemetry metrics and attaches standard semantic convention (`semconv`) attributes to network spans.

`TransportMetricsCtx` connects transport layer metrics with telemetry [crates/agentgateway/src/transport/stream.rs:92-96](). This allows tracing inbound and outbound flows consistently, correlating network metadata with agent identity and request attributes. The substrate layer thus acts as the bridge between low-level transport events and high-level observability.

For details, see [Substrate Ingress and Egress](#11.6).

Sources: [crates/agentgateway/src/transport/stream.rs:92-96]()

---

# Mapping Natural Language Concepts to Code Entities

To clarify how the system components correspond to specific code entities and protocols, the following diagrams relate natural language system concepts to the Rust code:

```mermaid
title Protocols and Connection Metadata - Code Mapping

graph LR
    TCP["TCP Socket"] -->|Encapsulated by| Socket["Socket struct"]
    Socket -->|Carries| TCPInfo["TCPConnectionInfo (peer/local IPs)"]
    Socket -->|Carries| TLSInfo["TLSConnectionInfo (mTLS, ALPN, SNI)"]
    Socket -->|Carries| HBONEInfo["HBONEConnectionInfo (Mesh Tunnel)"]
    Socket -->|Carries| MetricsCtx["TransportMetricsCtx (Telemetry labels)"]
```

```mermaid
title Transport Layer Operations - Code Mapping

graph TD
    Gateway["proxy::gateway::Gateway"] -->|Accept connections| TcpListener["std::net::TcpListener / Tokio"]
    TcpListener -->|Wrapped as| Socket["Socket (crates/agentgateway/src/transport/stream.rs)"]
    Socket -->|Protocol detection| Detect["Protocol Detection subsystem"]
    Detect -->|Dispatch| ProtocolHandlers["HTTP, TLS, PROXY, HBONE handlers"]
    
    Client["client::Client"] -->|Connection pooling| Pool["agent_pool crates"]
    Pool -->|Dial connections| Connector["client::Connector"]
    Connector -->|Use| Socket
    Socket -->|TLS wrapping| TLSWrap["Socket::from_tls"]
    Socket -->|HBONE tunneling| HboneTunnel["client::hbone_tunnel::handshake"]
```

Sources: [crates/agentgateway/src/transport/stream.rs:27-35](), [crates/agentgateway/src/transport/stream.rs:38-54](), [crates/agentgateway/src/transport/stream.rs:57-61](), [crates/agentgateway/src/transport/stream.rs:63-66](), [crates/agentgateway/src/transport/stream.rs:92-96](), [crates/agentgateway/src/transport/stream.rs:116-120](), [crates/agentgateway/src/transport/stream.rs:129-130](), [crates/agentgateway/src/transport/stream.rs:133-134](), [crates/agentgateway/src/transport/stream.rs:216-256]()

---

# Summary

The Network and Transport layer in agentgateway is foundational to reliably accepting diverse network protocols, providing transparent encryption, identity verification, and multiplexing streams efficiently. It abstractly manages connections through the polymorphic `Socket` type and integrates with advanced protocols like HBONE and the PROXY protocol. Connection pools optimize resource reuse and telemetry integration provides observability from transport events to the application layer.

This hierarchical network infrastructure supports complex multi-protocol workloads such as AI model connectivity, service mesh ingress/egress, and secure tenant routing, forming a bridge across OS-level transport and the rich proxy and gateway capabilities above.

For implementation details, consult the child pages listed at the top of this document.

---

