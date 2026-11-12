<!-- source: DeepWiki mcp.deepwiki.com · repo theagentrouter/agent-router · page 1 Overview · fetched 2026-10-21 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [site/docs/concepts/architecture/control-plane.md](site/docs/concepts/architecture/control-plane.md)
- [site/docs/concepts/architecture/data-plane.md](site/docs/concepts/architecture/data-plane.md)
- [site/docs/concepts/architecture/index.md](site/docs/concepts/architecture/index.md)
- [site/docs/concepts/architecture/system-architecture.md](site/docs/concepts/architecture/system-architecture.md)
- [site/docs/index.md](site/docs/index.md)
- [site/static/img/providers/anthropic.svg](site/static/img/providers/anthropic.svg)
- [site/static/img/providers/tars.svg](site/static/img/providers/tars.svg)
- [site/versioned_docs/version-0.1/index.md](site/versioned_docs/version-0.1/index.md)
- [site/versioned_docs/version-0.2/index.md](site/versioned_docs/version-0.2/index.md)
- [site/versioned_docs/version-0.3/index.md](site/versioned_docs/version-0.3/index.md)
- [site/versioned_docs/version-0.4/index.md](site/versioned_docs/version-0.4/index.md)

</details>



## Purpose and Scope

Agent Router (formerly known as *Envoy AI Gateway*) is an open-source control plane for AI and agent traffic powered by [Envoy](https://envoyproxy.io) and [Envoy Gateway](https://gateway.envoyproxy.io) [`README.md:11-13`(), `README.md:29-31`()]. It provides a consistent, OpenAI-compatible API for hosted LLMs, self-hosted inference backends, and Model Context Protocol (MCP) servers, allowing platform teams to manage credentials, routing, rate limiting, quotas, and failover centrally [`README.md:25`()]. 

This page provides a high-level overview of Agent Router's top-level architecture—covering the control plane controllers, the `extproc` data plane, the MCP proxy, the `aigw` CLI, and the documentation site—and links to its child pages for detailed technical deep-dives.

Sources: [`README.md:11-37`]()

---

## Top-Level Architecture

Agent Router operates in two primary deployment modes: as a Kubernetes control plane integrating with Envoy Gateway, and as a standalone local proxy via the `aigw` CLI [`README.md:43-50`(), `site/docs/concepts/architecture/control-plane.md:36-71`()]. 

```mermaid
graph TB
    subgraph NaturalLanguageSpace["Control and Data Plane Components"]
        CLI["\"aigw CLI Binary (cmd/aigw)\""]
        ControlPlane["\"Kubernetes Controller Manager (internal/controllers)\""]
        ExtServer["\"Envoy Gateway Extension Server (internal/extapi)\""]
        DataPlane["\"External Processor ExtProc (internal/extproc)\""]
        MCPProxy["\"MCP Gateway Proxy (internal/mcp)\""]
    end
    
    CLI --> DataPlane
    ControlPlane --> ExtServer
    ExtServer --> DataPlane
    DataPlane --> MCPProxy
```
*Figure 1: High-level architectural mapping of Agent Router subsystem components to codebase directories.*

Sources: [`go.mod:1-79`]()

---

### Control Plane Controllers
The Kubernetes control plane watches custom resources in the `aigateway.envoyproxy.io` API group (`AIGatewayRoute`, `AIServiceBackend`, `BackendSecurityPolicy`, `QuotaPolicy`) [`README.md:33`()]. It translates these high-level AI policies into Envoy Gateway resources (`HTTPRoute`, `HTTPRouteFilter`) and operates an extension server that fine-tunes xDS configurations [`site/docs/concepts/architecture/control-plane.md:61-68`(), `site/docs/concepts/architecture/control-plane.md:117-119`()].

Sources: [`site/docs/concepts/architecture/control-plane.md:36-108`]()

---

### ExtProc Data Plane
The data plane relies on Envoy Proxy paired with the AI Gateway External Processor (`extproc`) running as a sidecar container inside the Envoy Proxy Pod [`site/docs/concepts/architecture/control-plane.md:46-50`(), `site/docs/concepts/architecture/control-plane.md:123-123`()]. Communication between Envoy and the `extproc` sidecar occurs over a local Unix Domain Socket (UDS) for minimal latency [`site/docs/concepts/architecture/control-plane.md:123-123`()]. The processor executes a two-phase pipeline (Router-level and Upstream-level) handling model routing, provider authentication injection (such as AWS SigV4 or API keys), request/response transformation, and token usage extraction [`site/docs/concepts/architecture/data-plane.md:15-42`(), `site/docs/concepts/architecture/data-plane.md:121-124`()].

Sources: [`site/docs/concepts/architecture/data-plane.md:15-118`(), `site/docs/concepts/architecture/control-plane.md:122-124`]()

---

### MCP Proxy
Agent Router provides native support for the Model Context Protocol (MCP), enabling secure multiplexing of MCP servers, Server-Sent Events (SSE) streaming, tool/prompt merging, and claim-to-header authorization [`go.mod:32`()].

Sources: [`go.mod:32`]()

---

### CLI (`aigw`)
The `aigw` binary serves as the standalone runtime and developer interface [`README.md:46-49`()]. It allows operators to run Agent Router locally on Linux and macOS using `aigw run`, translate custom resources into Envoy Gateway manifests with `aigw translate`, and auto-configure providers from environment variables [`site/docs/getting-started/installation.md:18-19`(), `site/docs/getting-started/index.md:29-32`()].

Sources: [`site/docs/getting-started/installation.md:18-19`(), `site/docs/getting-started/index.md:29-32`]()

---

### Documentation Site
The documentation site is built with Docusaurus and resides in the `site/` directory [`site/docs/getting-started/installation.md:10`()]. It hosts user guides, concept explanations, API reference documentation generated via `make apidoc`, and versioned snapshots [`Makefile:113-123`()].

Sources: [`Makefile:113-123`(), `site/docs/getting-started/installation.md:10`]()

---

```mermaid
graph TB
    subgraph CodeEntitySpace["System Modules and Entities"]
        API["\"API Definitions (api/v1alpha1 & api/v1beta1)\""]
        Ctrl["\"Controller Manager (internal/controllers)\""]
        ExtProc["\"Data Plane ExtProc (internal/extproc)\""]
        CLIMod["\"CLI Runner (cmd/aigw)\""]
    end

    API --> Ctrl
    Ctrl --> ExtProc
    CLIMod --> ExtProc
```
*Figure 2: Component dependency flow linking API schemas, controllers, and the data plane processor.*

Sources: [`Makefile:103-110`(), `go.mod:1-79`]()

---

## Child Pages

For further details on specific topics, refer to the following child pages:

- **1.1. Getting Started and Installation** — Prerequisites, Helm install, basic usage, connecting providers, and examples directory walkthrough. For details, see [Getting Started and Installation](#1.1).
- **1.2. Repository Layout and Contributing** — Directory map, Makefile targets, codegen, contributing workflow, releases, and proposals. For details, see [Repository Layout and Contributing](#1.2).

Sources: [`CONTRIBUTING.md:1-135`(), `site/docs/getting-started/installation.md:1-81`]()

---

