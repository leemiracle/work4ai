<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/dcgm-exporter · page 6 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [internal/pkg/devicewatcher/device_watcher.go](internal/pkg/devicewatcher/device_watcher.go)
- [pkg/cmd/app.go](pkg/cmd/app.go)
- [security.md](security.md)

</details>



This page provides technical guidance for diagnosing and resolving issues within the DCGM Exporter. It covers the internal debugging facilities, health monitoring, and the handling of dynamic hardware events.

## Diagnostic Facilities

DCGM Exporter includes several built-in mechanisms for extracting state and performance data.

### Debug Dumps
The exporter can generate periodic state dumps to a specified directory. This is controlled by the following flags:
* `--dump-enabled`: Enables the dump facility [pkg/cmd/app.go:97]().
* `--dump-directory`: Sets the target path for dump files [pkg/cmd/app.go:98]().
* `--dump-retention`: Configures how many historical dumps to keep [pkg/cmd/app.go:99]().

### pprof Endpoints
When running, the exporter exposes standard Go `pprof` endpoints for profiling CPU usage, memory allocation, and goroutine blocking. These are typically available under the `/debug/pprof/` path on the configured listen address [internal/pkg/server/server.go:132-145]().

### DCGM Engine Logging
Internal DCGM engine logs can be redirected to the exporter's output.
* `--enable-dcgm-log`: Enables logging from the underlying DCGM shared library [pkg/cmd/app.go:90]().
* `--dcgm-log-level`: Sets the severity (e.g., `INFO`, `DEBUG`, `VERB`) [pkg/cmd/app.go:91]().

Sources: [pkg/cmd/app.go:88-105](), [internal/pkg/server/server.go:132-145]()

## Prerequisite Validation

At startup, the exporter performs a series of validations to ensure the environment is capable of providing metrics. This behavior can be bypassed using `--disable-startup-validate` [pkg/cmd/app.go:102]().

### Validation Logic
The `prerequisites` package checks for:
1. **Driver Presence**: Verification that NVIDIA drivers are loaded.
2. **DCGM Connectivity**: Ensuring `nv-hostengine` is reachable or the embedded hostengine can start.
3. **GPU Availability**: Confirming that at least one supported entity (GPU, NvSwitch, or CPU) is present.

```mermaid
title "Startup Validation Flow"
graph TD
    START["NewApp() Start"] --> PRE["prerequisites.Check()"]
    PRE --> DRV["Check NVIDIA Driver"]
    DRV --> HE["Check HostEngine Connection"]
    HE --> ENT["Check Entities (GPU/Switch/CPU)"]
    ENT -->|Success| RUN["Start HTTP Server"]
    ENT -->|Failure| ERR["Log Fatal & Exit"]
    
    subgraph "Validation Logic [internal/pkg/prerequisites/]"
        DRV
        HE
        ENT
    end
```
Sources: [pkg/cmd/app.go:102](), [internal/pkg/prerequisites/prerequisites.go:20-45]()

## Health Endpoint and Reloads

The `/health` endpoint provides status information, but its behavior changes during configuration reloads.

### Reloading Behavior
When a reload is triggered (via `SIGHUP` or a `ConfigMap` update), the exporter transitions through a state where the registry is being rebuilt.
* **X-Reload-In-Progress**: An HTTP header added to responses during a hot-reload [internal/pkg/server/server.go:180-185]().
* **X-Registry-Available**: Indicates if the metric registry is currently populated and ready for scraping [internal/pkg/server/server.go:187-192]().

### Implementation of Cleanup
During a reload or shutdown, the `DeviceWatcher` must release DCGM groups and field groups in a specific order to prevent resource leaks in the `nv-hostengine`.

| Step | Function | Description |
| :--- | :--- | :--- |
| 1 | `UnwatchFields` | Stops the DCGM engine from monitoring specific fields [internal/pkg/devicewatcher/device_watcher.go:57-67](). |
| 2 | `FieldGroupDestroy` | Deletes the logical grouping of field IDs [internal/pkg/devicewatcher/device_watcher.go:70-76](). |
| 3 | `DestroyGroup` | Deletes the logical grouping of GPU/Entity IDs [internal/pkg/devicewatcher/device_watcher.go:79-88](). |

Sources: [internal/pkg/server/server.go:180-195](), [internal/pkg/devicewatcher/device_watcher.go:45-89]()

## GPU Bind/Unbind Handling

In dynamic environments (like virtualized setups or certain HPC workloads), GPUs may be bound or unbound from the OS while the exporter is running.

### Monitoring Events
The exporter can watch for these events to avoid reporting stale data or failing when a device disappears.
* `--enable-gpu-bind-unbind-watch`: Enables the `DeviceWatchListManager` to monitor hardware changes [pkg/cmd/app.go:103]().
* `--gpu-bind-unbind-poll-interval`: Frequency of checking for device list changes [pkg/cmd/app.go:104]().

```mermaid
title "Hardware Event Handling"
graph LR
    subgraph "devicewatchlistmanager [internal/pkg/devicewatchlistmanager/]"
        POLLER["WatchLoop()"]
        DETECT["Detect Changes"]
    end
    
    subgraph "Registry Update"
        CLEAN["DeviceWatcher.Cleanup()"]
        REINIT["NewDeviceWatcher()"]
    end

    POLLER --> DETECT
    DETECT -->|"Device Unbound"| CLEAN
    DETECT -->|"Device Bound"| REINIT
    REINIT -->|"Update Registry"| REG["Registry.Update()"]
```
Sources: [pkg/cmd/app.go:103-104](), [internal/pkg/devicewatcher/device_watcher.go:125-167]()

## Common Error Codes

### DCGM Status Errors
The exporter handles specific DCGM return codes during the cleanup and watch process:
* `DCGM_ST_NOT_CONFIGURED`: Often occurs during shutdown if the connection to `nv-hostengine` is lost before the exporter finishes cleanup. These are logged as warnings but are generally benign [internal/pkg/devicewatcher/device_watcher.go:61-63]().
* `DCGM_ST_FIELD_NOT_WATCHED`: Occurs if an unwatch request is sent for a field that was already removed [internal/pkg/devicewatcher/device_watcher.go:62]().

### Metric Entity Mapping
If metrics are missing for specific entities, verify the `shouldIncludeField` logic. This function maps `Field_Entity_Group` types to ensure, for example, that CPU Core metrics are only requested for CPU entities [internal/pkg/devicewatcher/device_watcher.go:108-123]().

Sources: [internal/pkg/devicewatcher/device_watcher.go:50-89](), [internal/pkg/devicewatcher/device_watcher.go:108-123]()

---

