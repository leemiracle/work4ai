<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Relay · page 3 Plugin System · fetched 2026-10-26 -->

# Plugin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [crates/core/src/plugin.rs](crates/core/src/plugin.rs)
- [crates/core/tests/unit/plugin_tests.rs](crates/core/tests/unit/plugin_tests.rs)
- [docs/about-nemo-relay/concepts/plugins.mdx](docs/about-nemo-relay/concepts/plugins.mdx)
- [docs/build-plugins/about.mdx](docs/build-plugins/about.mdx)
- [docs/configure-plugins/about.mdx](docs/configure-plugins/about.mdx)
- [docs/configure-plugins/nemo-guardrails/about.mdx](docs/configure-plugins/nemo-guardrails/about.mdx)
- [docs/configure-plugins/nemo-guardrails/configuration.mdx](docs/configure-plugins/nemo-guardrails/configuration.mdx)
- [docs/configure-plugins/plugin-configuration-files.mdx](docs/configure-plugins/plugin-configuration-files.mdx)
- [docs/getting-started/configuration.mdx](docs/getting-started/configuration.mdx)
- [docs/index.yml](docs/index.yml)
- [docs/resources/glossary.mdx](docs/resources/glossary.mdx)

</details>



The NeMo Relay plugin system provides a modular architecture to manage reusable runtime behaviors—such as custom middleware, execution intercepts, and telemetry subscribers—through declarative configuration files and programmatic registrations [crates/core/src/plugin.rs:4-10](). By abstracting configuration validation, activation lifecycles, and rollback bookkeeping, plugins allow applications and CLI gateways to extend Relay uniformly across languages and execution models [crates/core/src/plugin.rs:4-10]().

This page serves as a high-level overview of the plugin subsystem, covering static components, configuration formats, native dynamic plugins, and gRPC worker plugins. For in-depth technical details, refer to the child pages linked throughout.

---

## 3.1. Plugin Registration and Configuration

The NeMo Relay plugin infrastructure relies on a canonical configuration document type, `PluginConfig`, which structures the schema version, an ordered list of components, and fallback policies for unrecognized options [crates/core/src/plugin.rs:139-153](). Each entry in the component list is represented by a `PluginComponentSpec`, identifying its stable string kind, enablement status, and configuration payload [crates/core/src/plugin.rs:166-172]().

Plugins implement the core `Plugin` trait, which defines configuration validation (`validate`) and runtime registration (`register`) methods [crates/core/tests/unit/plugin_tests.rs:177-196](). During startup, Relay passes a `PluginRegistrationContext` to enabled components, safely tracking all installed middleware and subscribers to support atomic rollbacks if setup fails [crates/core/src/plugin.rs:408-415]().

For detailed information on the `Plugin` trait, `PluginConfig`, `ComponentSpec`, `PluginContext`, activation reports, validation policies, configuration editors, and `plugins.toml` file discovery rules, see [Plugin Registration and Configuration](#3.1).

Sources:
- [crates/core/src/plugin.rs:4-10]()
- [crates/core/src/plugin.rs:139-153]()
- [crates/core/src/plugin.rs:166-172]()
- [crates/core/src/plugin.rs:408-415]()
- [crates/core/tests/unit/plugin_tests.rs:177-196]()

---

## 3.2. Dynamic Plugins (Native)

NeMo Relay supports dynamic native plugins that extend the core runtime with functionality packaged inside external shared libraries [crates/core/src/plugin/dynamic/native.rs:4-5](). These components load directly into the Relay host process via `libloading`, eliminating inter-process serialization overhead and providing minimal callback latency for performance-critical middleware [docs/build-plugins/about.mdx:39-40]().

The control plane uses `DynamicPluginRecord` entries [docs/configure-plugins/plugin-configuration-files.mdx:145-153]() and `relay-plugin.toml` manifests to manage binary compatibility contracts, attestation modes, startup entry points, and lifecycle reconciliation between the registry and the host [docs/about-nemo-relay/concepts/plugins.mdx:44-45]().

For detailed coverage of `DynamicPluginRecord`, `relay-plugin.toml` manifests, compatibility contracts, attestation modes, startup classes, registry/host reconciliation, and in-process native shared-library loading, see [Dynamic Plugins (Native)](#3.2).

Sources:
- [crates/core/src/plugin/dynamic/native.rs:4-5]()
- [docs/about-nemo-relay/concepts/plugins.mdx:44-45]()
- [docs/build-plugins/about.mdx:39-40]()
- [docs/configure-plugins/plugin-configuration-files.mdx:145-153]()

---

## 3.3. Worker Plugins and the gRPC Protocol

Worker plugins execute in isolated separate processes, communicating with the NeMo Relay core over a language-neutral gRPC interface [docs/build-plugins/about.mdx:39-41](). This delivery model provides strict dependency isolation and robust crash boundaries, making it ideal for plugins written in Python or other runtimes that should not risk destabilizing the main application process [docs/build-plugins/about.mdx:42-43]().

Communication follows the `grpc-v1` worker protocol (`nemo.relay.worker.v1`), supported by dedicated developer kits such as the Rust `crates/worker` SDK and the Python `nemo-relay-plugin` SDK [docs/build-plugins/about.mdx:65-66](). These libraries handle the underlying worker lifecycle, protocol serialization, codec identity, and asynchronous event streams.

For complete specifications on the `grpc-v1` worker protocol, `crates/worker` SDK, `worker-proto`, Python plugin SDK (`nemo-relay-plugin`), worker lifecycle, and codec identity, see [Worker Plugins and the gRPC Protocol](#3.3).

Sources:
- [crates/core/src/plugin/dynamic/worker.rs:4-5]()
- [docs/build-plugins/about.mdx:39-43]()
- [docs/build-plugins/about.mdx:65-66]()

---

## 3.4. Plugin Examples and Language-Binding Plugins

Language-binding plugins run directly inside the application process using host bindings for Rust, Python, or Node.js [docs/build-plugins/about.mdx:38-40](). They provide the simplest authoring and distribution experience for application-owned hooks, interceptors, and custom event observers [docs/build-plugins/about.mdx:48-52]().

The codebase provides concrete implementations under `examples/` demonstrating these various approaches, including `rust-native-plugin`, `rust-grpc-worker-plugin`, `python-grpc-worker-plugin`, and multi-language `language-binding-plugin` packages [docs/build-plugins/about.mdx:38-48]().

For a full walkthrough of these example projects, multi-language bindings, and registration behavior guides, see [Plugin Examples and Language-Binding Plugins](#3.4).

Sources:
- [docs/build-plugins/about.mdx:38-48]()

---

## Plugin Architecture Overview

Title: "Plugin Architecture Component Flow"
```mermaid
flowchart TB
subgraph "Configuration Space"
    PC[""PluginConfig (crates/core/src/plugin.rs:139-153)""]
    PCS[""PluginComponentSpec (crates/core/src/plugin.rs:166-172)""]
    PC --> PCS
end
subgraph "Core Runtime"
    PT[""Plugin Trait (crates/core/tests/unit/plugin_tests.rs:177-196)""]
    PRC[""PluginRegistrationContext (crates/core/src/plugin.rs:408-415)""]
    PCS --> PT
    PT --> PRC
end
subgraph "Dynamic and Worker Layer"
    DPR[""DynamicPluginRecord (crates/core/src/plugin/dynamic/native.rs:4-5)""]
    WPA[""WorkerPluginActivation (crates/core/src/plugin/dynamic/worker.rs:153-156)""]
end
PC -.-> DPR
```

Sources:
- [crates/core/src/plugin.rs:139-153]()
- [crates/core/src/plugin.rs:166-172]()
- [crates/core/src/plugin.rs:408-415]()
- [crates/core/src/plugin/dynamic/native.rs:4-5]()
- [crates/core/src/plugin/dynamic/worker.rs:153-156]()
- [crates/core/tests/unit/plugin_tests.rs:177-196]()

---

## Plugin Execution Models

Title: "Plugin Execution Models"
```mermaid
flowchart LR
subgraph "Host Process"
    A[""Language-Binding / Native Plugin (crates/core/src/plugin.rs:58-62)""]
end
subgraph "Worker Process"
    B[""gRPC Worker Plugin (nemo.relay.worker.v1)""]
end
A -->|"In-Process Call"| C[""Runtime API Registry (crates/core/src/api/registry.rs)""]
B -->|"gRPC Transport"| C
```

Sources:
- [crates/core/src/plugin.rs:58-62]()

---

