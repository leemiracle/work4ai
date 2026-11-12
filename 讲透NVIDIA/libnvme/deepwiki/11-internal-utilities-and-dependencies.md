<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/libnvme · page 11 Internal Utilities and Dependencies · fetched 2026-10-26 -->

# Internal Utilities and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ccan/meson.build](ccan/meson.build)
- [internal/meson.build](internal/meson.build)
- [meson.build](meson.build)
- [src/meson.build](src/meson.build)
- [src/nvme/log.c](src/nvme/log.c)
- [src/nvme/log.h](src/nvme/log.h)
- [src/nvme/no-json.c](src/nvme/no-json.c)

</details>



The `libnvme` codebase relies on a set of internal support libraries and utility modules to manage common C programming tasks such as data structure management, logging, and resource cleanup. These utilities provide a consistent foundation for both `libnvme.so` and `libnvme-mi.so`.

The internal infrastructure is primarily composed of the bundled **CCAN** library for core data structures and a set of internal helpers for logging and RAII-style memory management.

### Dependency Relationship Overview

The following diagram illustrates how the core libraries interact with internal utilities and optional external dependencies.

**Internal Dependency Mapping**
```mermaid
graph TD
    subgraph "Public Libraries"
        [libnvme.so]
        [libnvme-mi.so]
    end

    subgraph "Internal Utilities"
        CCAN["ccan (static)"]
        LOG["nvme/log.c"]
        CLEANUP["nvme/cleanup.c"]
        STUBS["nvme/no-json.c"]
    end

    subgraph "External Dependencies (Optional)"
        JSONC["json-c"]
        OPENSSL["openssl"]
        DBUS["libdbus"]
    end

    [libnvme.so] --> CCAN
    [libnvme.so] --> LOG
    [libnvme.so] --> CLEANUP
    
    [libnvme-mi.so] --> CCAN
    [libnvme-mi.so] --> LOG
    
    [libnvme.so] -.-> JSONC
    [libnvme.so] -.-> OPENSSL
    [libnvme-mi.so] -.-> DBUS
    
    JSONC -.-> STUBS
```
**Sources:**
- [src/meson.build:49-59]() (libnvme linking with libccan and deps)
- [src/meson.build:78-88]() (libnvme-mi linking with libccan and mi_deps)
- [src/meson.build:27-31]() (Conditional inclusion of json.c or no-json.c)

---

### CCAN Utility Library

`libnvme` bundles specific components from the **C Code Archive Network (CCAN)** to provide robust, header-only or lightweight implementations of common C patterns. These are compiled into a static library `libccan` which is then linked into the main shared objects.

Key components used include:
*   **ccan/list**: Provides the circular doubly-linked list implementation used for all topology objects (e.g., tracking controllers under a subsystem).
*   **ccan/str**: Safe string manipulation and debugging utilities.
*   **ccan/endian**: Macros for byte-order conversion, essential for NVMe's little-endian specification requirements.
*   **ccan/container_of**: Standard macro for retrieving a pointer to a containing structure.

For details, see [CCAN Utility Library](#11.1).

**Sources:**
- [ccan/meson.build:9-13]() (CCAN source files)
- [ccan/meson.build:20-26]() (Static library definition for libccan)
- [meson.build:134-199]() (Feature detection for CCAN requirements like `typeof` and `endian`)

---

### Logging, Cleanup, and Stubs

The library implements a unified logging system and internal helpers to simplify resource management and handle optional feature sets.

#### Logging Infrastructure
The logging system is centered around the `nvme_root_t` context. It supports configurable log levels, PID logging, and timestamps. The core entry point is `nvme_init_logging`, which configures how the `__nvme_msg` macro (internal) outputs data to `stderr` or a user-defined file pointer.

#### Resource Cleanup (RAII)
`libnvme` uses GCC/Clang `__cleanup__` attributes to implement RAII-like behavior in C. This ensures that memory (like `asprintf` buffers) and file descriptors are automatically released when they go out of scope, reducing memory leak risks in complex error paths.

#### Feature Stubs
To maintain a stable ABI even when optional dependencies like `json-c` are missing, the library uses "stub" files. For example, `no-json.c` provides empty implementations of configuration functions that return `-ENOTSUP`.

For details, see [Logging, Cleanup, and No-JSON Stubs](#11.2).

**Sources:**
- [src/nvme/log.h:28-36]() (nvme_init_logging definition)
- [src/nvme/log.c:29-85]() (__nvme_msg implementation)
- [src/nvme/no-json.c:13-27]() (JSON stub implementations)
- [src/nvme/log.c:47-48]() (Usage of `__cleanup__` attribute)

---

### Build-time Configuration
The internal utilities are heavily influenced by the build-time environment detected by Meson. The `config.h` file tracks available compiler features and library presence.

| Feature | Code Entity | Purpose |
| :--- | :--- | :--- |
| **JSON Support** | `CONFIG_JSONC` | Determines if `json.c` or `no-json.c` is compiled. |
| **MCTP Support** | `CONFIG_LIBMCTP` | Enables NVMe-MI over MCTP transport. |
| **Endianness** | `HAVE_LITTLE_ENDIAN` | Configures `ccan/endian` for the target architecture. |
| **OpenSSL** | `CONFIG_OPENSSL` | Enables DH-HMAC-CHAP and TLS PSK derivation. |

**Sources:**
- [meson.build:66-67]() (JSON-C config)
- [meson.build:102-103]() (OpenSSL config)
- [meson.build:180-188]() (Endianness detection)
- [internal/meson.build:12-15]() (Generation of config.h)

---

