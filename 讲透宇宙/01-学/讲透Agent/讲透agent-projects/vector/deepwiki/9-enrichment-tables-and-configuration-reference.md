<!-- source: DeepWiki mcp.deepwiki.com · repo vectordotdev/vector · page 9 Enrichment Tables and Configuration Reference · fetched 2026-10-29 -->

# Enrichment Tables and Configuration Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [changelog.d/25143_enrichment_table_memory_cuckoo_filter.feature.md](changelog.d/25143_enrichment_table_memory_cuckoo_filter.feature.md)
- [changelog.d/25154_enrichment_table_memory_bloom_filter.feature.md](changelog.d/25154_enrichment_table_memory_bloom_filter.feature.md)
- [changelog.d/tls_server_name_openssl_verify.fix.md](changelog.d/tls_server_name_openssl_verify.fix.md)
- [lib/vector-common/src/internal_event/metric_name.rs](lib/vector-common/src/internal_event/metric_name.rs)
- [lib/vector-core/src/tls/incoming.rs](lib/vector-core/src/tls/incoming.rs)
- [lib/vector-core/src/tls/mod.rs](lib/vector-core/src/tls/mod.rs)
- [lib/vector-core/src/tls/reload.rs](lib/vector-core/src/tls/reload.rs)
- [lib/vector-core/src/tls/settings.rs](lib/vector-core/src/tls/settings.rs)
- [src/enrichment_tables/file.rs](src/enrichment_tables/file.rs)
- [src/enrichment_tables/geoip.rs](src/enrichment_tables/geoip.rs)
- [src/enrichment_tables/memory/bloom_table.rs](src/enrichment_tables/memory/bloom_table.rs)
- [src/enrichment_tables/memory/config.rs](src/enrichment_tables/memory/config.rs)
- [src/enrichment_tables/memory/cuckoo_table.rs](src/enrichment_tables/memory/cuckoo_table.rs)
- [src/enrichment_tables/memory/internal_events.rs](src/enrichment_tables/memory/internal_events.rs)
- [src/enrichment_tables/memory/mod.rs](src/enrichment_tables/memory/mod.rs)
- [src/enrichment_tables/memory/table.rs](src/enrichment_tables/memory/table.rs)
- [src/enrichment_tables/mmdb.rs](src/enrichment_tables/mmdb.rs)
- [src/enrichment_tables/mod.rs](src/enrichment_tables/mod.rs)
- [src/http.rs](src/http.rs)
- [website/cue/reference/generated/configuration.cue](website/cue/reference/generated/configuration.cue)
- [website/cue/reference/remap/functions.cue](website/cue/reference/remap/functions.cue)

</details>



This section provides a high-level overview of Vector's enrichment table system and its global configuration framework. Vector allows users to augment event data in real-time using external datasets and provides a unified configuration schema for controlling the global behavior of the pipeline.

## Enrichment Tables

Enrichment tables are external data sources that can be queried during event processing, typically via [Vector Remap Language (VRL) functions](https://vector.dev/docs/reference/vrl/functions/#enrichment). They allow for tasks such as GeoIP lookups, user ID to metadata mapping, or CIDR block identification.

Vector supports several types of enrichment tables:

| Table Type | Description | Key Code Entities |
| :--- | :--- | :--- |
| **File (CSV)** | Loads data from local CSV files into memory. Supports schema coercion (e.g., `string` to `integer`). | `FileConfig` [src/enrichment_tables/file.rs:69](), `FileSettings` [src/enrichment_tables/file.rs:53]() |
| **GeoIP** | Optimized for MaxMind GeoIP2 and GeoLite2 databases. Supports localized names. | `GeoipConfig` [src/enrichment_tables/geoip.rs:52](), `Geoip` [src/enrichment_tables/geoip.rs:111]() |
| **MMDB** | A generic reader for any MaxMind DB format file, supporting custom object mapping. | `MmdbConfig` [src/enrichment_tables/mmdb.rs:19](), `Mmdb` [src/enrichment_tables/mmdb.rs:46]() |
| **In-Memory** | Populated dynamically from Vector sources. Supports TTL, max byte sizes, and probabilistic filters (Cuckoo/Bloom). | `MemoryConfig` [src/enrichment_tables/memory/config.rs:34](), `Memory` [src/enrichment_tables/memory/table.rs:119]() |

All enrichment tables are managed by a registry system that handles the lifecycle and access for VRL functions. Tables implement the `Table` trait [src/enrichment_tables/mod.rs:6]() to provide standardized lookup methods like `find_table_row` [src/enrichment_tables/mmdb.rs:104-119](). The `EnrichmentTables` enum [src/enrichment_tables/mod.rs:48-69]() acts as the top-level container for these configurations.

For details, see [Enrichment Tables](#9.1).

### Enrichment Table System Architecture

The following diagram illustrates how enrichment tables are defined in configuration and registered for use by the VRL runtime.

**Enrichment Table Registration and Lookup**
```mermaid
graph TD
    subgraph "Configuration Space"
        [EnrichmentTables_Enum] --> [FileConfig]
        [EnrichmentTables_Enum] --> [GeoipConfig]
        [EnrichmentTables_Enum] --> [MemoryConfig]
        [EnrichmentTables_Enum] --> [MmdbConfig]
    end

    subgraph "Runtime Space"
        [TableRegistry]
        [Table_Trait]
        [VRL_Runtime]
    end

    [FileConfig] -->|builds| [Table_Trait]
    [GeoipConfig] -->|builds| [Table_Trait]
    [MemoryConfig] -->|builds| [Table_Trait]
    [MmdbConfig] -->|builds| [Table_Trait]
    
    [Table_Trait] -->|registered in| [TableRegistry]
    [VRL_Runtime] -->|invokes find_table_row| [TableRegistry]
```
**Sources:** [src/enrichment_tables/mod.rs:4-69](), [src/enrichment_tables/file.rs:67-72](), [src/enrichment_tables/geoip.rs:100-116](), [src/enrichment_tables/mmdb.rs:35-42](), [src/enrichment_tables/memory/table.rs:119-127]()

## Global Configuration and TLS

The global configuration controls the fundamental behavior of the Vector instance. These settings apply to all components unless explicitly overridden.

### Key Global Options
*   **`data_dir`**: The primary directory where Vector persists state, including disk buffers and file checkpoints.
*   **`api`**: Configuration for the Vector API, including bind address and enablement status [website/cue/reference/generated/configuration.cue:5-30]().
*   **`enrichment_tables`**: Global definitions for external datasets [website/cue/reference/generated/configuration.cue:31-33]().

### TLS and Networking
Vector provides a standardized TLS framework used across both sources and sinks. This includes support for certificate authority (CA) chains, client-side certificates for mutual TLS (mTLS), and ALPN protocols [lib/vector-core/src/tls/settings.rs:89-161](). The `HttpClient` utility provides a proxy-aware TLS connector built from Vector's `MaybeTlsSettings` and `ProxyConfig` [src/http.rs:83-118]().

For details, see [Global Configuration and TLS](#9.2).

**Sources:** [website/cue/reference/generated/configuration.cue:1-30](), [lib/vector-core/src/tls/settings.rs:46-161](), [src/http.rs:83-118]()

## Documentation and Schema System

Vector utilizes a CUE-based documentation and schema system to ensure that the Rust implementation, the configuration specification, and the public-facing documentation remain in sync.

### CUE-Based Metadata
The generated CUE metadata defines the structure of Vector's configuration [website/cue/reference/generated/configuration.cue:3-4](). This schema is used to:
1.  Validate configuration files against defined types and enums.
2.  Generate documentation for the [Vector website](https://vector.dev).
3.  Define default values and examples for all component options [website/cue/reference/generated/configuration.cue:9-10]().

### Code-to-Schema Mapping
Vector uses the `configurable_component` macro in Rust to export component metadata [src/enrichment_tables/file.rs:67](). This metadata is then processed to generate the CUE definitions. The `GenerateConfig` trait [src/enrichment_tables/geoip.rs:90-98]() is implemented by configuration structs to provide example outputs for documentation.

**Natural Language to Code Entity Space: Configuration**
```mermaid
graph LR
    subgraph "User Documentation (Natural Language)"
        [Vector_Dev_Docs]
        [Config_Examples]
    end

    subgraph "Metadata & Schema (CUE)"
        [configuration_cue]
        [remap_functions_cue]
    end

    subgraph "Rust Implementation (Code Entities)"
        [TlsConfig_Struct]
        [configurable_component_Macro]
        [GenerateConfig_Trait]
        [EnrichmentTableConfig_Trait]
    end

    [TlsConfig_Struct] -->|annotated with| [configurable_component_Macro]
    [configurable_component_Macro] -->|extracted to| [configuration_cue]
    [configuration_cue] -->|renders| [Vector_Dev_Docs]
    [GenerateConfig_Trait] -->|provides| [Config_Examples]
    [EnrichmentTableConfig_Trait] -->|defines build logic| [TlsConfig_Struct]
```
**Sources:** [website/cue/reference/generated/configuration.cue:1-30](), [src/enrichment_tables/file.rs:67-69](), [src/enrichment_tables/geoip.rs:90-98](), [lib/vector-core/src/tls/settings.rs:89-91](), [website/cue/reference/remap/functions.cue:3-61]()

---

