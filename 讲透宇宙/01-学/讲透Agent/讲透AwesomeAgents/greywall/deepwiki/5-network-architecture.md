<!-- source: DeepWiki mcp.deepwiki.com · repo GreyhavenHQ/greywall · page 5 Network Architecture · fetched 2026-10-26 -->

# Network Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/proxy/detect.go](internal/proxy/detect.go)
- [internal/proxy/install.go](internal/proxy/install.go)
- [internal/proxy/start.go](internal/proxy/start.go)
- [internal/sandbox/color.go](internal/sandbox/color.go)
- [internal/sandbox/linux.go](internal/sandbox/linux.go)
- [internal/sandbox/linux_features_stub.go](internal/sandbox/linux_features_stub.go)

</details>



This document provides a comprehensive overview of greywall's network isolation architecture. It explains how sandboxed processes are prevented from making unauthorized network connections, how traffic is routed through the greyproxy filtering proxy, and the platform-specific implementations on Linux and macOS.

For details on the greyproxy service itself (installation, configuration, dashboard), see [greyproxy Service](#5.1). For implementation details of Unix socket bridges on Linux, see [Proxy Bridges and Unix Sockets](#5.2). For domain-based filtering rules and allow/deny lists, see [Domain-Based Filtering](#5.3).

For the complete Linux sandboxing implementation including filesystem and syscall controls, see [Linux Sandboxing](#4.1). For macOS sandboxing details, see [macOS Sandboxing](#4.2).

## Overview

Greywall implements network isolation through a two-layer architecture:

1. **Sandbox Layer**: Platform-specific mechanisms (network namespaces on Linux, Seatbelt profiles on macOS) that isolate the sandboxed process from the host network stack.
2. **Proxy Layer**: The greyproxy service that provides centralized traffic filtering, domain-based allow/deny rules, and an optional upstream SOCKS5 proxy chain.

All network traffic from sandboxed processes is routed through greyproxy, which listens on localhost ports 43052 (SOCKS5), 43051 (HTTP CONNECT), and 43053 (DNS). The dashboard runs on port 43080.

**Key Design Principles:**

- **Deny-by-default**: Network access is blocked unless explicitly allowed via greyproxy's domain filtering rules.
- **Transparent on Linux**: Network redirection happens at the kernel level using TUN devices and network namespaces, requiring no application awareness.
- **Environment-based on macOS**: Applications must respect `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` environment variables.
- **Centralized filtering**: All traffic converges at greyproxy regardless of platform, enabling consistent policy enforcement.

Sources: [internal/sandbox/linux.go:21-41](), [internal/proxy/detect.go:15-18]()

## Two-Layer Network Isolation

```mermaid
graph TB
    subgraph "Sandboxed Process"
        APP["Application Code"]
        NETCALL["Network Request<br/>(connect/bind/socket)"]
    end
    
    subgraph "Layer 1: OS Sandbox Isolation"
        LINUX_NS["Linux: Network Namespace<br/>--unshare-net<br/>Isolated network stack"]
        MACOS_SEATBELT["macOS: Seatbelt Profile<br/>network-outbound rules<br/>Environment variables"]
    end
    
    subgraph "Layer 2: greyproxy Filtering"
        GP_SOCKS["SOCKS5 Server<br/>localhost:43052"]
        GP_HTTP["HTTP CONNECT<br/>localhost:43051"]
        GP_DNS["DNS Server<br/>localhost:43053"]
        GP_RULES["Domain Rules Engine<br/>allowedDomains<br/>deniedDomains"]
    end
    
    subgraph "External Network"
        INTERNET["Internet"]
        UPSTREAM["Optional Upstream SOCKS5<br/>(configured via --proxy)"]
    end
    
    APP --> NETCALL
    
    NETCALL -->|"Linux path"| LINUX_NS
    NETCALL -->|"macOS path"| MACOS_SEATBELT
    
    LINUX_NS --> GP_SOCKS
    LINUX_NS --> GP_DNS
    MACOS_SEATBELT --> GP_SOCKS
    MACOS_SEATBELT --> GP_HTTP
    
    GP_SOCKS --> GP_RULES
    GP_HTTP --> GP_RULES
    GP_DNS --> GP_RULES
    
    GP_RULES -->|"allowed"| INTERNET
    GP_RULES -->|"denied"| APP
    GP_RULES -.->|"optional chain"| UPSTREAM
    UPSTREAM --> INTERNET
```

**Layer 1** isolates the sandboxed process from the host network using platform-specific OS mechanisms. On Linux, this creates a completely separate network namespace with no connectivity except through controlled bridges. On macOS, Seatbelt profiles restrict network operations and environment variables point applications to the proxy.

**Layer 2** provides application-layer filtering through greyproxy. All traffic that escapes Layer 1 must pass through greyproxy's domain-based filtering, which maintains allow/deny lists and provides real-time traffic inspection via the dashboard.

Sources: [internal/sandbox/linux.go:21-41](), [internal/proxy/detect.go:30-36]()

## Platform-Specific Implementations

### Linux: Transparent Network Proxying

Linux achieves transparent network proxying through a sophisticated multi-component system that requires no application cooperation:

```mermaid
graph TB
    subgraph "Inside Network Namespace"
        APP["Sandboxed Process"]
        TUNDEV["TUN Device: tun0<br/>IP: 198.18.0.1/15<br/>Default gateway"]
        T2S["tun2socks Process<br/>gvisor netstack<br/>Packet -> SOCKS5 conversion"]
        SOCAT_PROXY["socat Process<br/>TCP :18321 -> Unix socket"]
        SOCAT_DNS["socat Process<br/>UDP :53 -> Unix socket"]
        SOCAT_REV["socat Processes<br/>Unix socket -> SOCKS5"]
    end
    
    subgraph "Host Side (Outside Namespace)"
        PROXY_SOCK["ProxyBridge Unix Socket<br/>/tmp/greywall-proxy-*.sock"]
        DNS_SOCK["DnsBridge Unix Socket<br/>/tmp/greywall-dns-*.sock"]
        REV_SOCK["ReverseBridge Unix Sockets<br/>/tmp/greywall-rev-*-*.sock"]
        GP["greyproxy Service<br/>localhost:43052/43051/43053"]
    end
    
    APP -->|"All network traffic"| TUNDEV
    TUNDEV -->|"Raw IP packets"| T2S
    T2S -->|"SOCKS5 to 127.0.0.1:18321"| SOCAT_PROXY
    APP -->|"DNS queries to :53"| SOCAT_DNS
    APP -->|"Inbound connections"| SOCAT_REV
    
    SOCAT_PROXY -.->|"Crosses namespace boundary"| PROXY_SOCK
    SOCAT_DNS -.->|"Crosses namespace boundary"| DNS_SOCK
    SOCAT_REV -.->|"Crosses namespace boundary"| REV_SOCK
    
    PROXY_SOCK --> GP
    DNS_SOCK --> GP
    REV_SOCK --> GP
```

**Component Breakdown:**

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| **Network Namespace** | Complete network isolation via `--unshare-net` | Created by bubblewrap, loopback-only by default |
| **TUN Device (tun0)** | Virtual network interface as default route | 198.18.0.1/15 address, created inside namespace |
| **tun2socks** | Converts raw IP packets to SOCKS5 proxy requests | Uses gvisor netstack, binds to SOCKS5 at 127.0.0.1:18321 |
| **ProxyBridge** | Bridges SOCKS5 traffic across namespace boundary | `socat` relay: TCP :18321 -> Unix socket -> greyproxy |
| **DnsBridge** | Bridges DNS queries across namespace boundary | `socat` relay: UDP :53 -> Unix socket -> greyproxy DNS |
| **ReverseBridge** | Enables inbound connections for dev servers | `socat` relay: Unix socket -> SOCKS5 for exposed ports |

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:36-41](), [internal/sandbox/linux.go:105-111](), [internal/sandbox/linux_features_stub.go:13-29]()

### macOS: Environment Variable Proxy Configuration

macOS uses a simpler approach based on proxy environment variables, as macOS `sandbox-exec` does not support network namespace isolation:

```mermaid
graph LR
    subgraph "Sandboxed Process"
        APP["Application"]
        ENV["Environment Variables:<br/>HTTP_PROXY=http://localhost:43051<br/>HTTPS_PROXY=http://localhost:43051<br/>ALL_PROXY=socks5://localhost:43052"]
    end
    
    subgraph "Host Network Stack"
        GP["greyproxy Service<br/>SOCKS5: :43052<br/>HTTP CONNECT: :43051"]
    end
    
    APP --> ENV
    ENV -->|"Application must<br/>respect proxy vars"| GP
```

**Key Differences from Linux:**

- No transparent proxying capability (applications must respect proxy environment variables).
- DNS queries cannot be reliably intercepted (no DNS bridge).
- No network namespace isolation (relies on Seatbelt `network-outbound` rules).

Sources: [internal/sandbox/linux_features_stub.go:63-71]()

## Network Traffic Flow

The following sequence diagram shows the complete flow of a network request from a sandboxed process to the external network on Linux:

```mermaid
sequenceDiagram
    participant App as "Sandboxed Process"
    participant Namespace as "Network Namespace"
    participant TUN as "TUN Device tun0"
    participant T2S as "tun2socks"
    participant Socat as "socat Bridge"
    participant UnixSock as "Unix Socket"
    participant Greyproxy as "greyproxy Service"
    
    App->>Namespace: connect("example.com", 443)
    Namespace->>TUN: Route via default gateway (198.18.0.1)
    TUN->>T2S: Raw IP packet
    T2S->>T2S: Parse packet, extract destination
    T2S->>Socat: SOCKS5 CONNECT example.com:443
    Socat->>UnixSock: Forward to Unix socket
    UnixSock->>Greyproxy: SOCKS5 request
    
    Note over Greyproxy: Apply Domain Rules
    
    Greyproxy->>Internet: Establish connection
```

Sources: [internal/sandbox/linux.go:65-69](), [internal/sandbox/linux.go:175-179]()

## Component Architecture

### ProxyBridge (Linux)

The `ProxyBridge` struct manages the Unix socket bridge between the network namespace and the host-side greyproxy service.

```mermaid
graph LR
    subgraph "ProxyBridge Creation"
        NEW["NewProxyBridge()"]
        PARSE["parseProxyURL()"]
        SOCK["Generate SocketPath"]
        SOCAT["exec.Command(socat)"]
    end
    
    subgraph "ProxyBridge Entity"
        SOCKET["SocketPath string"]
        HOST["ProxyHost string"]
        PORT["ProxyPort string"]
        PROC["process *exec.Cmd"]
    end
    
    NEW --> PARSE
    PARSE --> SOCK
    SOCK --> SOCAT
    SOCAT --> PROC
```

**Key Methods:**

- `NewProxyBridge()` - Creates bridge, starts `socat`, waits for socket file [internal/sandbox/linux.go:141-200]().
- `Cleanup()` - Kills `socat` process, removes socket file [internal/sandbox/linux.go:203-213]().
- `parseProxyURL()` - Validates and parses SOCKS5 URL [internal/sandbox/linux.go:216-224]().

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:141-213]()

### DnsBridge (Linux)

The `DnsBridge` provides DNS resolution inside the network namespace by bridging UDP DNS queries to the host-side greyproxy DNS server.

**Key Methods:**

- `NewDnsBridge()` - Creates a Unix socket bridge to a host-side DNS server [internal/sandbox/linux.go:44-90]().
- `Cleanup()` - Stops the DNS bridge and removes the socket file [internal/sandbox/linux.go:93-103]().

Sources: [internal/sandbox/linux.go:36-41](), [internal/sandbox/linux.go:44-103]()

### greyproxy Service Integration

The greyproxy service is a separate binary that greywall depends on. It is automatically installed and managed by greywall.

| Operation | Code Path | Description |
|-----------|-----------|-------------|
| **Detection** | `proxy.Detect()` | Checks if greyproxy is installed and running via health endpoint [internal/proxy/detect.go:43-63](). |
| **Installation** | `proxy.Install()` | Downloads latest release from GitHub, extracts, and installs [internal/proxy/install.go:87-153](). |
| **Starting** | `proxy.Start()` | Runs `greyproxy service start` [internal/proxy/start.go:11-30](). |
| **Health Check** | `proxy.checkRunning()` | Hits `http://localhost:43080/api/health` [internal/proxy/detect.go:95-126](). |

The greyproxy health endpoint returns a `healthResponse` struct [internal/proxy/detect.go:31-36]().

Sources: [internal/proxy/detect.go:1-127](), [internal/proxy/install.go:1-153](), [internal/proxy/start.go:1-30]()

## Network Configuration

### Default Ports and URLs

Greywall uses the following defaults for network monitoring and proxying:

- **Health URL**: `http://localhost:43080/api/health` [internal/proxy/detect.go:16]().
- **GitHub Repository**: `greyhavenhq/greyproxy` [internal/proxy/install.go:21-22]().

### Proxy URL Configuration

The `ProxyBridge` captures credentials from the proxy URL if provided:
- `ProxyUser`: Username from ProxyURL [internal/sandbox/linux.go:26]().
- `ProxyPass`: Password from ProxyURL [internal/sandbox/linux.go:27]().
- `HasAuth`: Boolean indicating if credentials were provided [internal/sandbox/linux.go:28]().

Sources: [internal/sandbox/linux.go:22-31](), [internal/sandbox/linux.go:168-172]()

---

