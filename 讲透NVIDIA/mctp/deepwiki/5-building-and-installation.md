<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/mctp · page 5 Building and Installation · fetched 2026-10-26 -->

# Building and Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [meson.build](meson.build)
- [tests/pytest.ini](tests/pytest.ini)
- [tests/requirements.txt](tests/requirements.txt)

</details>



## Purpose and Scope

This page provides an overview of the build and installation process for the MCTP userspace tools. It covers the high-level workflow, quick start instructions, build artifacts, and installation procedures. For detailed information about specific aspects of the build system:

- Build system internals and Meson configuration: see [Build System](#5.1)
- Compile-time options and feature flags: see [Build Options and Configuration](#5.2)
- Required and optional dependencies: see [Dependencies](#5.3)

## Build Workflow Overview

The MCTP project uses Meson as its build system, which orchestrates compilation of multiple executables from shared and executable-specific source files. The build process involves configuration detection, dependency resolution, compilation, optional test execution, and installation.

```mermaid
flowchart TD
    START["Developer/User"]
    
    subgraph "Configuration Phase"
        SETUP["meson setup obj<br/>Configure build directory"]
        DETECT["Dependency Detection"]
        CONFCHECK["Configuration Checks"]
        GENCONFIG["Generate config.h"]
        
        SETUP --> DETECT
        DETECT --> CONFCHECK
        CONFCHECK --> GENCONFIG
    end
    
    subgraph "Compilation Phase"
        COMPILE["ninja -C obj<br/>Compile sources"]
        UTIL["Compile mctp-util.c"]
        NETLINK["Compile mctp-netlink.c"]
        OPS["Compile mctp-ops.c"]
        MAIN["Compile main sources"]
        LINK["Link executables"]
        
        COMPILE --> UTIL
        COMPILE --> NETLINK
        COMPILE --> OPS
        COMPILE --> MAIN
        UTIL --> LINK
        NETLINK --> LINK
        OPS --> LINK
        MAIN --> LINK
    end
    
    subgraph "Output Artifacts"
        MCTP_BIN["obj/mctp"]
        MCTPD_BIN["obj/mctpd"]
        TOOLS["obj/mctp-req<br/>obj/mctp-echo<br/>obj/mctp-bench<br/>obj/mctp-client"]
        TEST_BIN["obj/test-mctpd<br/>obj/test-mctp"]
    end
    
    subgraph "Testing Phase"
        TEST["meson test -C obj"]
        PYTEST["pytest execution"]
        DBUS_ISO["dbus-run-session isolation"]
        
        TEST --> DBUS_ISO
        DBUS_ISO --> PYTEST
    end
    
    subgraph "Installation Phase"
        INSTALL["meson install -C obj"]
        DEST_BIN["/usr/local/bin/<br/>mctp, mctp-client"]
        DEST_SBIN["/usr/local/sbin/<br/>mctpd"]
        
        INSTALL --> DEST_BIN
        INSTALL --> DEST_SBIN
    end
    
    START --> SETUP
    GENCONFIG --> COMPILE
    LINK --> MCTP_BIN
    LINK --> MCTPD_BIN
    LINK --> TOOLS
    LINK --> TEST_BIN
    TEST_BIN --> TEST
    MCTP_BIN --> INSTALL
    MCTPD_BIN --> INSTALL
    TOOLS --> INSTALL
```

**Sources:** [meson.build:1-174](), [README.md:15-36]()

## Quick Start

### Basic Build

To configure and compile the project with default settings:

```bash
meson setup obj
ninja -C obj
```

The `meson setup` command creates a build directory (`obj`) and performs configuration checks. The `ninja -C obj` command compiles all source files and links the executables.

### Build Without Tests

If you don't need the test suite and want to avoid test dependencies:

```bash
meson setup obj -Dtests=false
ninja -C obj
```

### Installation

To install to the default prefix (`/usr/local`):

```bash
meson install -C obj
```

To install with a custom `DESTDIR` (useful for packaging):

```bash
DESTDIR=/tmp/staging meson install -C obj
```

**Sources:** [README.md:18-28]()

## Build Artifacts

The build process produces multiple executables, each serving different purposes in the MCTP ecosystem:

```mermaid
flowchart LR
    subgraph "Source Files"
        MCTP_C["src/mctp.c"]
        MCTPD_C["src/mctpd.c"]
        REQ_C["src/mctp-req.c"]
        ECHO_C["src/mctp-echo.c"]
        BENCH_C["src/mctp-bench.c"]
        CLIENT_C["src/mctp-client.c"]
        
        subgraph "Shared Sources"
            UTIL_C["src/mctp-util.c"]
            NETLINK_C["src/mctp-netlink.c"]
            OPS_C["src/mctp-ops.c"]
            TEST_OPS_C["tests/mctp-ops-test.c"]
        end
    end
    
    subgraph "Production Binaries"
        MCTP_BIN["mctp<br/>CLI utility<br/>Installed to bin/"]
        MCTPD_BIN["mctpd<br/>Daemon<br/>Installed to sbin/<br/>Requires libsystemd"]
        REQ_BIN["mctp-req<br/>Request tool<br/>Not installed"]
        ECHO_BIN["mctp-echo<br/>Echo responder<br/>Not installed"]
        BENCH_BIN["mctp-bench<br/>Benchmarking<br/>Not installed"]
        CLIENT_BIN["mctp-client<br/>Client tool<br/>Installed to bin/"]
    end
    
    subgraph "Test Binaries"
        TEST_MCTP["test-mctp<br/>CLI test variant<br/>Uses mock sockets"]
        TEST_MCTPD["test-mctpd<br/>Daemon test variant<br/>Uses mock sockets<br/>Requires libsystemd"]
    end
    
    MCTP_C --> MCTP_BIN
    MCTP_C --> TEST_MCTP
    MCTPD_C --> MCTPD_BIN
    MCTPD_C --> TEST_MCTPD
    REQ_C --> REQ_BIN
    ECHO_C --> ECHO_BIN
    BENCH_C --> BENCH_BIN
    CLIENT_C --> CLIENT_BIN
    
    UTIL_C --> MCTP_BIN
    UTIL_C --> MCTPD_BIN
    UTIL_C --> TEST_MCTP
    UTIL_C --> TEST_MCTPD
    UTIL_C --> REQ_BIN
    UTIL_C --> ECHO_BIN
    UTIL_C --> BENCH_BIN
    UTIL_C --> CLIENT_BIN
    
    NETLINK_C --> MCTP_BIN
    NETLINK_C --> MCTPD_BIN
    NETLINK_C --> TEST_MCTP
    NETLINK_C --> TEST_MCTPD
    
    OPS_C --> MCTP_BIN
    OPS_C --> MCTPD_BIN
    
    TEST_OPS_C --> TEST_MCTP
    TEST_OPS_C --> TEST_MCTPD
```

### Production Executables

| Executable | Purpose | Installation Path | Dependencies |
|------------|---------|-------------------|--------------|
| `mctp` | Command-line utility for kernel MCTP stack management | `${prefix}/bin/mctp` | None |
| `mctpd` | MCTP control protocol daemon and bus owner | `${prefix}/sbin/mctpd` | libsystemd ≥ 247 |
| `mctp-client` | Client utility for MCTP communication | `${prefix}/bin/mctp-client` | None |
| `mctp-req` | Request/response test utility | Not installed | None |
| `mctp-echo` | Echo responder for testing | Not installed | None |
| `mctp-bench` | Performance benchmarking tool | Not installed | None |

### Test Executables

| Executable | Purpose | Differences from Production |
|------------|---------|----------------------------|
| `test-mctp` | Test variant of `mctp` utility | Uses `mctp-ops-test.c` for mock socket operations instead of `mctp-ops.c` |
| `test-mctpd` | Test variant of `mctpd` daemon | Uses `mctp-ops-test.c` for mock socket operations instead of `mctp-ops.c` |

The test executables are functionally identical to their production counterparts, except they use a mock socket implementation that communicates via Unix domain sockets. This allows the test suite to simulate kernel MCTP behavior without requiring actual kernel support.

**Sources:** [meson.build:46-100]()

## Installation Locations

The installation layout follows standard Unix conventions:

```mermaid
flowchart TD
    PREFIX["Installation Prefix<br/>Default: /usr/local"]
    
    BIN["${prefix}/bin/<br/>User executables"]
    SBIN["${prefix}/sbin/<br/>System executables"]
    SYSCONFDIR["${prefix}/etc/<br/>Configuration"]
    
    MCTP_BIN["mctp"]
    CLIENT_BIN["mctp-client"]
    MCTPD_BIN["mctpd"]
    CONFFILE["mctpd.conf<br/>Default path"]
    
    PREFIX --> BIN
    PREFIX --> SBIN
    PREFIX --> SYSCONFDIR
    
    BIN --> MCTP_BIN
    BIN --> CLIENT_BIN
    SBIN --> MCTPD_BIN
    SYSCONFDIR --> CONFFILE
```

### Configuration File Location

The `mctpd` daemon expects its configuration file at `${prefix}/etc/mctpd.conf` by default. This path is compiled into the binary via the `MCTPD_CONF_FILE_DEFAULT` preprocessor definition. You can override this at runtime using the `-c FILE` command-line option.

### Example Installation Paths

For the default prefix (`/usr/local`):
- `mctp` → `/usr/local/bin/mctp`
- `mctp-client` → `/usr/local/bin/mctp-client`
- `mctpd` → `/usr/local/sbin/mctpd`
- Configuration → `/usr/local/etc/mctpd.conf`

For a system installation with prefix `/usr`:
- `mctp` → `/usr/bin/mctp`
- `mctp-client` → `/usr/bin/mctp-client`
- `mctpd` → `/usr/sbin/mctpd`
- Configuration → `/etc/mctpd.conf`

**Sources:** [meson.build:36-39, 56-91]()

## Testing the Build

The project includes an integration test suite that validates both the `mctp` utility and the `mctpd` daemon. Tests are enabled by default but can be disabled with `-Dtests=false`.

### Test Infrastructure Overview

```mermaid
flowchart TB
    subgraph "Test Execution"
        MESON_TEST["meson test -C obj"]
        SH["sh wrapper script"]
        DBUS_SESSION["dbus-run-session"]
        PYTEST["pytest runner"]
        
        MESON_TEST --> SH
        SH --> DBUS_SESSION
        DBUS_SESSION --> PYTEST
    end
    
    subgraph "Test Isolation"
        DBUS_ISO["Isolated D-Bus session"]
        ENV_VARS["DBUS_STARTER_BUS_TYPE=user"]
        UNIX_SOCKS["Unix domain socket mocks"]
        
        DBUS_SESSION --> DBUS_ISO
        DBUS_SESSION --> ENV_VARS
        PYTEST --> UNIX_SOCKS
    end
    
    subgraph "Test Binaries"
        TEST_MCTPD["test-mctpd<br/>Uses mctp-ops-test.c"]
        TEST_MCTP["test-mctp<br/>Uses mctp-ops-test.c"]
    end
    
    subgraph "Test Files"
        TEST_MCTPD_PY["tests/test_mctpd.py"]
        TEST_ENDPOINT_PY["tests/test_mctpd_endpoint.py"]
        TEST_MCTP_PY["tests/test_mctp.py"]
        CONFTEST["tests/conftest.py<br/>Fixtures"]
        PYTEST_INI["tests/pytest.ini<br/>Configuration"]
    end
    
    subgraph "Mock Environment"
        MCTPENV["tests/mctpenv/<br/>Simulation infrastructure"]
        SYS_SIM["System state simulation"]
        NET_SIM["Network simulation"]
        SOCK_SIM["Socket operation mocks"]
    end
    
    PYTEST --> TEST_MCTPD_PY
    PYTEST --> TEST_ENDPOINT_PY
    PYTEST --> TEST_MCTP_PY
    PYTEST --> CONFTEST
    PYTEST --> PYTEST_INI
    
    TEST_MCTPD_PY --> TEST_MCTPD
    TEST_ENDPOINT_PY --> TEST_MCTPD
    TEST_MCTP_PY --> TEST_MCTP
    
    CONFTEST --> MCTPENV
    MCTPENV --> SYS_SIM
    MCTPENV --> NET_SIM
    MCTPENV --> SOCK_SIM
    
    TEST_MCTPD --> SOCK_SIM
    TEST_MCTP --> SOCK_SIM
```

### Running Tests

**Via Meson:**
```bash
meson test -C obj
```

This runs all configured tests with proper isolation.

**Via pytest directly (for development):**
```bash
cd obj
dbus-run-session env DBUS_STARTER_BUS_TYPE=user pytest
```

**With a Python virtual environment:**
```bash
python3 -m venv venv
venv/bin/pip install -r tests/requirements.txt
PATH=$PWD/venv/bin/:$PATH meson setup obj
ninja -C obj test
```

### Test Categories

The test suite includes three main test targets:

| Test Target | Source File | Tests |
|-------------|-------------|-------|
| `test-mctpd` | [tests/test_mctpd.py]() | Core mctpd daemon functionality, D-Bus interfaces, control protocol handling |
| `test-mctpd-endpoint` | [tests/test_mctpd_endpoint.py]() | Endpoint management, EID assignment, recovery mechanisms |
| `test-mctp` | [tests/test_mctp.py]() | CLI utility operations, Netlink interactions |

### Test Isolation

Tests run in an isolated environment to prevent interference with the system:

1. **D-Bus Isolation:** Each test run uses `dbus-run-session` to create an isolated D-Bus session, preventing test behaviors from affecting applications on the system bus.

2. **Socket Mocking:** Test binaries (`test-mctpd`, `test-mctp`) use mock socket operations from [tests/mctp-ops-test.c]() that communicate over Unix domain sockets instead of real Netlink and MCTP sockets.

3. **Environment Simulation:** The [tests/mctpenv/]() directory provides simulated system state (interfaces, routes, neighbors) and network endpoints.

**Sources:** [meson.build:102-173](), [README.md:113-149](), [tests/pytest.ini:1-6](), [tests/requirements.txt:1-7]()

## Conditional Compilation

### libsystemd Dependency

The `mctpd` daemon requires `libsystemd` (version ≥ 247) and is only compiled if this dependency is found:

```mermaid
flowchart TD
    BUILD["Build Process"]
    CHECK{"libsystemd ≥ 247<br/>found?"}
    
    BUILD --> CHECK
    CHECK -->|Yes| MCTPD["Build mctpd<br/>Build test-mctpd<br/>Enable mctpd tests"]
    CHECK -->|No| SKIP["Skip mctpd<br/>Skip test-mctpd<br/>Skip mctpd tests"]
    
    MCTPD --> MCTP["Always build mctp<br/>and supporting tools"]
    SKIP --> MCTP
```

The detection is performed at [meson.build:17]() using `dependency('libsystemd', version: '>=247', required: false)`. If libsystemd is not found, the build continues but without the daemon components.

### Test Suite

Tests are controlled by the `tests` Meson option (enabled by default). When disabled, pytest and Python dependencies are not required, and test executables are not built.

**Sources:** [meson.build:17, 83-100, 102-103](), [README.md:31-36]()

## Configuration File Generation

During the configuration phase, Meson generates a `config.h` header file that defines preprocessor macros based on system capabilities and build options:

| Macro | Detection Method | Purpose |
|-------|------------------|---------|
| `HAVE_LINUX_MCTP_H` | `cc.has_header('linux/mctp.h')` | Indicates kernel MCTP header availability |
| `HAVE_STRUCT_MCTP_FQ_ADDR` | `cc.has_type('struct mctp_fq_addr', ...)` | Indicates support for flow-qualified addresses |
| `MCTPD_RECOVER_NIL_UUID` | `get_option('unsafe-recover-nil-uuid')` | Enables nil UUID handling in recovery |
| `MCTPD_WRITABLE_CONNECTIVITY` | `get_option('unsafe-writable-connectivity')` | Enables writable Connectivity property |
| `MCTPD_CONF_FILE_DEFAULT` | Path construction | Default configuration file path |

The generated header is used by all compiled sources to adapt to the build environment.

**Sources:** [meson.build:19-44]()

## Integration with System Services

While the build system handles compilation and installation, the repository includes example systemd service files under the `conf/` directory (not installed by default). These files coordinate:

- Local MCTP stack setup (interfaces, addresses)
- Supervision of the `mctpd` process
- Integration with the system D-Bus daemon

For production deployment, these configuration files should be installed to the appropriate systemd directories (typically `/etc/systemd/system/` or `/usr/lib/systemd/system/`).

**Sources:** [README.md:27-29, 68-71]()

---

