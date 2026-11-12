<!-- source: DeepWiki mcp.deepwiki.com · repo steel-dev/steel-browser · page 15 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [api/.prettierrc](api/.prettierrc)
- [api/src/services/cdp/errors/launch-errors.ts](api/src/services/cdp/errors/launch-errors.ts)
- [api/src/services/cdp/utils/error-handlers.ts](api/src/services/cdp/utils/error-handlers.ts)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT_SETUP.md](docs/DEVELOPMENT_SETUP.md)
- [docs/README.md](docs/README.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [images/star_img.png](images/star_img.png)
- [render.yaml](render.yaml)

</details>



This page provides solutions for common issues encountered when using Steel Browser, along with debugging techniques to help diagnose and resolve problems.

## Error Handling Architecture

Steel Browser implements a structured error handling system with categorized error types and automatic retries. Understanding this system helps diagnose issues more effectively.

### Error Categorization System

The `CDPService` and associated utilities categorize launch failures into specific types defined in [api/src/services/cdp/errors/launch-errors.ts:6-17](). Each error type inherits from `BaseLaunchError` [api/src/services/cdp/errors/launch-errors.ts:77-100](), which includes an `isRetryable` flag.

| Error Type | Retryable | Common Causes |
|------------|-----------|---------------|
| `TIMEOUT` | Yes | Browser launch exceeds the 30s timeout [api/src/services/cdp/errors/launch-errors.ts:106-118]() |
| `CONFIGURATION` | No | Invalid dimensions, timezone, or proxy URL [api/src/services/cdp/errors/launch-errors.ts:124-142]() |
| `RESOURCE` | Varies | Missing Chrome binary, extension loading failures [api/src/services/cdp/errors/launch-errors.ts:148-163]() |
| `SYSTEM` | Yes | File access or OS-level operation failures [api/src/services/cdp/errors/launch-errors.ts:169-182]() |
| `NETWORK` | Yes | Port binding or WebSocket setup failures [api/src/services/cdp/errors/launch-errors.ts:188-200]() |
| `BROWSER_PROCESS` | Yes | Process crashes during launch or target setup [api/src/services/cdp/errors/launch-errors.ts:267-281]() |
| `FINGERPRINT` | Yes | Failures during fingerprint generation or injection [api/src/services/cdp/errors/launch-errors.ts:206-218]() |

Sources: [api/src/services/cdp/errors/launch-errors.ts:6-281]()

### Execution Wrappers

The codebase uses specific wrappers to handle errors based on their criticality:

*   **`executeCritical`**: Executes operations that MUST succeed. Throws categorized errors on failure [api/src/services/cdp/utils/error-handlers.ts:18-27]().
*   **`executeOptional`**: Logs a warning but continues execution if the operation fails [api/src/services/cdp/utils/error-handlers.ts:46-59]().
*   **`executeBestEffort`**: Silently logs debug info and continues on failure [api/src/services/cdp/utils/error-handlers.ts:76-87]().

Sources: [api/src/services/cdp/utils/error-handlers.ts:1-88]()

## Common Issues & Solutions

### 1. Browser Launch Failures

#### Symptoms
*   "Failed to launch browser" errors in logs.
*   Chrome executable not found.
*   Permission denied errors.

#### Solutions
**Verify Chrome Path**: Ensure `CHROME_EXECUTABLE_PATH` is set correctly for your OS [README.md:148-155]().
*   **Linux**: `/usr/bin/google-chrome`
*   **MacOS**: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
*   **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`

**Linux Dependencies**: If running on Linux, ensure system dependencies for Chromium are installed [docs/TROUBLESHOOTING.md:65-77]().

```mermaid
graph TD
    subgraph "Code Entity Space"
        B_UTIL["api/src/utils/browser.ts"]
        CDP_S["api/src/services/cdp/cdp.service.ts"]
        ERR_H["api/src/services/cdp/utils/error-handlers.ts"]
    end

    subgraph "Natural Language Space"
        START["Request Launch"]
        FIND["Find Chrome Path"]
        EXEC["Spawn Process"]
        FAIL["Launch Error"]
    end

    START --> CDP_S
    CDP_S -- "calls" --> B_UTIL
    B_UTIL -- "checks env" --> FIND
    CDP_S -- "uses" --> ERR_H
    ERR_H -- "wraps" --> EXEC
    EXEC -- "throws" --> FAIL
```
Sources: [README.md:134-155](), [docs/TROUBLESHOOTING.md:41-87](), [api/src/services/cdp/utils/error-handlers.ts:18-27]()

### 2. Docker & Container Issues

#### Symptoms
*   Container fails to start or crashes immediately.
*   "Out of memory" errors in container logs.

#### Solutions
*   **Memory Limits**: Increase Node.js memory if sessions crash [docs/TROUBLESHOOTING.md:122-123]().
*   **Platform Flags**: For Mac Silicon (M1/M2/M3) users, use `DOCKER_DEFAULT_PLATFORM=linux/arm64` when running `docker compose` [README.md:104-106]().
*   **Zombie Processes**: The entrypoint script `api/entrypoint.sh` is designed to handle process reaping; ensure it is being used [Dockerfile:125]().

Sources: [README.md:104-106](), [docs/TROUBLESHOOTING.md:112-132](), [Dockerfile:118-125]()

### 3. Network & Proxy Issues

#### Symptoms
*   Cannot reach external websites.
*   Proxy authentication failures.

#### Solutions
*   **Proxy Config**: Set `PROXY_URL` with the format `http://username:password@host:port` [docs/TROUBLESHOOTING.md:143-145]().
*   **Health Check**: Use the health endpoint to verify the API is reachable: `curl http://localhost:3000/v1/health` [docs/TROUBLESHOOTING.md:11]().

Sources: [docs/TROUBLESHOOTING.md:133-152](), [render.yaml:6]()

## Debugging Techniques

### Enabling Verbose Logs
To diagnose deep issues within the CDP or browser process, set the following environment variables:
*   `ENABLE_VERBOSE_LOGGING=true` [docs/TROUBLESHOOTING.md:208]()
*   `ENABLE_CDP_LOGGING=true` [docs/TROUBLESHOOTING.md:209]()
*   `DEBUG_CHROME_PROCESS=true` [docs/TROUBLESHOOTING.md:236]()

### System Diagnostics
Use these commands to inspect the state of the host or container:

| Command | Purpose |
|---------|---------|
| `ps aux \| grep chrome` | Check for orphaned Chrome processes [docs/TROUBLESHOOTING.md:308]() |
| `lsof -i :3000` | Check if the API port is occupied [docs/TROUBLESHOOTING.md:100]() |
| `df -h` | Check for disk space issues (logs/cache) [docs/TROUBLESHOOTING.md:169]() |

```mermaid
flowchart TD
    subgraph "System State"
        PROC["OS Processes"]
        NET["Network Ports"]
        DISK["Disk Storage"]
    end

    subgraph "Steel Entities"
        CDP["CDPService"]
        SESS["SessionService"]
        FILE["FileService"]
    end

    CDP -- "manages" --> PROC
    SESS -- "binds" --> NET
    FILE -- "writes" --> DISK

    DIAG["Troubleshooting Guide"]
    DIAG -- "recommends" --> PS["ps aux"]
    DIAG -- "recommends" --> LSOF["lsof"]
    DIAG -- "recommends" --> DF["df -h"]

    PS -.-> PROC
    LSOF -.-> NET
    DF -.-> DISK
```
Sources: [docs/TROUBLESHOOTING.md:89-111](), [docs/TROUBLESHOOTING.md:154-176](), [docs/TROUBLESHOOTING.md:301-311]()

## Log Analysis Patterns

When reviewing logs, look for these specific patterns to identify the source of failure:

*   **`[CDPService] ... - continuing with launch`**: Indicates an error was caught by `executeOptional`. The launch will likely succeed, but a specific feature (like a plugin or cleanup) failed [api/src/services/cdp/utils/error-handlers.ts:56]().
*   **`Browser process error (launch_failed)`**: Indicates the binary failed to execute. Check `CHROME_PATH` [api/src/services/cdp/errors/launch-errors.ts:21]().
*   **`Network error during websocket setup`**: Indicates the browser started but the API cannot connect to its debugging port [api/src/services/cdp/errors/launch-errors.ts:59]().

Sources: [api/src/services/cdp/utils/error-handlers.ts:46-59](), [api/src/services/cdp/errors/launch-errors.ts:19-62]()

---

