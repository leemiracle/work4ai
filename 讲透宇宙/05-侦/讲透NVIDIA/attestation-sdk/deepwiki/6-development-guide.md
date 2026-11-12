<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/attestation-sdk · page 6 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [nv-attestation-cli/CMakeLists.txt](nv-attestation-cli/CMakeLists.txt)
- [nv-attestation-sdk-cpp/CMakeLists.txt](nv-attestation-sdk-cpp/CMakeLists.txt)

</details>



This guide provides essential information for developers working on the NVIDIA Attestation SDK codebase. It covers the build system, development environment setup, code quality standards, testing infrastructure, and contribution workflows. This page serves as an overview; more detailed information on specific topics can be found in the child pages.

**Scope**: This guide focuses on SDK and CLI development workflows. For information about:
- Building and installing as an end user, see [Installation Guide](#2.1)
- Using the SDK in your own applications, see [Architecture](#3)
- SDK API reference, see [Reference](#8)
- Contribution requirements and PR process, see [Contributing](#7)

---

## Development Environment Components

The development environment consists of multiple interconnected systems that support building, testing, and maintaining code quality:

```mermaid
graph TB
    subgraph "Developer Workstation"
        SOURCE["Source Code<br/>C++ SDK + CLI"]
        CMAKE["CMake Build System<br/>CMakeLists.txt"]
        TOOLS["Development Tools"]
    end
    
    subgraph "Build Tools"
        COMPILER["C++ Compiler<br/>C++14 Standard"]
        RUST["Rust Toolchain<br/>For regorus-ffi"]
        DEPS["System Dependencies<br/>CURL, OpenSSL, LibXml2,<br/>spdlog, xmlsec"]
    end
    
    subgraph "Code Quality Tools"
        FORMAT["clang-format<br/>.clang-format config"]
        TIDY["clang-tidy<br/>.clang-tidy config"]
        WARNINGS["Compiler Warnings<br/>-Wall -Wextra -Wpedantic"]
    end
    
    subgraph "Testing Framework"
        GTEST["Google Test<br/>Unit & Integration Tests"]
        TEST_DATA["Test Data<br/>Evidence Files + Policies"]
        ENV_VARS["Environment Variables<br/>TEST_MODE, TEST_DEVICES"]
    end
    
    subgraph "Optional Hardware Support"
        NVML["NVML Library<br/>GPU Attestation"]
        NSCQ["NSCQ Library<br/>Switch Attestation"]
    end
    
    SOURCE --> CMAKE
    CMAKE --> COMPILER
    CMAKE --> RUST
    CMAKE --> DEPS
    CMAKE --> NVML
    CMAKE --> NSCQ
    
    SOURCE --> FORMAT
    SOURCE --> TIDY
    COMPILER --> WARNINGS
    
    CMAKE --> GTEST
    GTEST --> TEST_DATA
    GTEST --> ENV_VARS
    
    NVML -.->|"Optional<br/>ENABLE_NVML=ON"| CMAKE
    NSCQ -.->|"Optional<br/>ENABLE_NSCQ=ON"| CMAKE
```

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:1-273](), [nv-attestation-cli/CMakeLists.txt:1-70](), [CONTRIBUTING.md:10-74]()

---

## Build System Architecture

The project uses CMake with a two-tier structure: the core SDK library (`nvat`) and the CLI tool (`nvattest`) that depends on it.

### Build Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `BUILD_SHARED_LIBS` | Boolean | `ON` | Build shared libraries instead of static |
| `BUILD_TESTING` | Boolean | `OFF` | Enable test compilation |
| `BUILD_EXAMPLES` | Boolean | `OFF` | Build example executables |
| `ENABLE_NVML` | Boolean | `OFF` | Enable GPU attestation via NVML |
| `ENABLE_NSCQ` | Boolean | `OFF` | Enable switch attestation via NSCQ |
| `SANITIZER` | String | `OFF` | Enable sanitizer (`thread`, `address`, `undefined`, `leak`) |
| `CMAKE_BUILD_TYPE` | String | - | Build type (`Debug`, `Release`, etc.) |
| `CMAKE_COMPILE_WARNING_AS_ERROR` | Boolean | `ON` | Treat compiler warnings as errors |

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:12-17](), [nv-attestation-cli/CMakeLists.txt:4]()

### CMake Target Dependencies

```mermaid
graph TD
    subgraph "CLI Build (nv-attestation-cli)"
        CLI_TARGET["nvattest executable<br/>src/main.cpp<br/>src/version.cpp<br/>src/attest.cpp"]
    end
    
    subgraph "SDK Build (nv-attestation-sdk-cpp)"
        SDK_TARGET["nvat library<br/>src/nvat.cpp<br/>src/attestation.cpp<br/>src/verify.cpp<br/>+ 20+ source files"]
        
        SDK_SOURCES["Core Sources<br/>claims, RIM, SPDM,<br/>GPU/Switch modules"]
        
        SDK_HEADERS["Public Headers<br/>include/nvat.h.in<br/>→ include/nvat.h"]
    end
    
    subgraph "Rust Dependencies"
        REGORUS_FFI["regorus_ffi<br/>Static Library<br/>bindings/ffi/Cargo.toml"]
    end
    
    subgraph "Fetched Dependencies"
        CLI11["CLI11<br/>Command-line parsing"]
        JWT_CPP["jwt-cpp<br/>JWT token handling"]
        JSON["nlohmann/json<br/>JSON parsing"]
    end
    
    subgraph "System Dependencies"
        SPDLOG["spdlog<br/>Logging"]
        OPENSSL["OpenSSL<br/>Crypto + SSL"]
        CURL["CURL<br/>HTTP client"]
        LIBXML2["LibXml2<br/>XML parsing"]
        XMLSEC["xmlsec<br/>XML signatures"]
    end
    
    subgraph "Optional Dependencies"
        NVML_LIB["NVML<br/>GPU management"]
        NSCQ_LIB["NSCQ<br/>Switch query"]
    end
    
    CLI_TARGET --> SDK_TARGET
    CLI_TARGET --> CLI11
    CLI_TARGET --> JSON
    CLI_TARGET --> SPDLOG
    
    SDK_TARGET --> SDK_SOURCES
    SDK_TARGET --> SDK_HEADERS
    SDK_TARGET --> REGORUS_FFI
    SDK_TARGET --> JWT_CPP
    SDK_TARGET --> JSON
    SDK_TARGET --> SPDLOG
    SDK_TARGET --> OPENSSL
    SDK_TARGET --> CURL
    SDK_TARGET --> LIBXML2
    SDK_TARGET --> XMLSEC
    
    SDK_TARGET -.->|"ENABLE_NVML=ON"| NVML_LIB
    SDK_TARGET -.->|"ENABLE_NSCQ=ON"| NSCQ_LIB
    
    REGORUS_FFI -.->|"Generates header<br/>before build"| SDK_TARGET
```

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:123-216](), [nv-attestation-cli/CMakeLists.txt:27-57]()

### Build Directory Structure

After a typical build, the directory structure looks like:

```
build/
├── nv-attestation-sdk-build/          # SDK library build artifacts
│   ├── include/nvat.h                  # Generated public header
│   ├── libnvat.so                      # Shared library (or .a if static)
│   ├── unit-tests/                     # SDK unit tests
│   └── integration-tests/              # SDK integration tests
├── nvattest                            # CLI executable
├── config.toml                         # Copied config file
├── version_config.h                    # Generated version header
└── tests/                              # CLI tests
    └── cli_tests
```

The CLI build includes the SDK as a subdirectory via `add_subdirectory()` at [nv-attestation-cli/CMakeLists.txt:44-47](). This creates an alias target `nvat::nvat` for linking.

**Sources**: [nv-attestation-cli/CMakeLists.txt:44-50](), [nv-attestation-sdk-cpp/CMakeLists.txt:123-158]()

---

## Code Quality Standards

The project enforces strict code quality through multiple mechanisms working together:

### Compiler Warnings

The build system enables comprehensive warnings treated as errors:

```mermaid
graph LR
    SOURCE["Source Files"]
    
    subgraph "Compiler Flags"
        STANDARD["-std=c++14"]
        WARNINGS["-Wall -Wextra<br/>-Wpedantic"]
        ERROR["-Werror<br/>Warnings → Errors"]
        UNUSED["-Wno-unused<br/>-Wno-unused-parameter"]
        FILE_PREFIX["-ffile-prefix-map<br/>Relative paths in logs"]
    end
    
    subgraph "Conditional Flags"
        DEBUG["-g3 -O0<br/>-fno-omit-frame-pointer"]
        SANITIZER_FLAGS["-fsanitize=TYPE<br/>-fno-sanitize-recover=all"]
    end
    
    SOURCE --> STANDARD
    SOURCE --> WARNINGS
    SOURCE --> ERROR
    SOURCE --> UNUSED
    SOURCE --> FILE_PREFIX
    
    DEBUG -.->|"Debug build or<br/>Sanitizer enabled"| SOURCE
    SANITIZER_FLAGS -.->|"SANITIZER option"| SOURCE
```

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:4-119](), [nv-attestation-cli/CMakeLists.txt:7-11]()

### Code Formatting with clang-format

Code formatting is enforced through `clang-format` with a project-specific `.clang-format` configuration file. Developers must format code before committing:

| Command | Purpose |
|---------|---------|
| `git-clang-format --style file [commit]` | Format git changes (staged if no commit specified) |
| `clang-format -style=file -i <files>` | Format individual files in-place |

**Key formatting rules enforced**:
- Class, function, method, variable, and field naming conventions
- Comment style consistency
- Indentation rules
- Line length limits

**Sources**: [CONTRIBUTING.md:16-33]()

### Build-Time Validation

The CMake configuration enforces quality at build time:

```mermaid
flowchart TD
    START["Build Initiated<br/>cmake --build build"]
    
    CHECK_STD["Check C++ Standard<br/>CMAKE_CXX_STANDARD = 14"]
    CHECK_WARN["Compile with Warnings<br/>-Wall -Wextra -Wpedantic"]
    
    ERROR_CHECK{"Warnings Found?"}
    
    FAIL_BUILD["Build Fails<br/>CMAKE_COMPILE_WARNING_AS_ERROR=ON"]
    
    SANITIZER_CHECK{"Sanitizer Enabled?"}
    SANITIZER_RUN["Run with Sanitizer<br/>-fsanitize=TYPE"]
    
    SUCCESS["Build Succeeds<br/>Artifacts Generated"]
    
    START --> CHECK_STD
    CHECK_STD --> CHECK_WARN
    CHECK_WARN --> ERROR_CHECK
    
    ERROR_CHECK -->|"Yes"| FAIL_BUILD
    ERROR_CHECK -->|"No"| SANITIZER_CHECK
    
    SANITIZER_CHECK -->|"Yes"| SANITIZER_RUN
    SANITIZER_CHECK -->|"No"| SUCCESS
    
    SANITIZER_RUN --> SUCCESS
```

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:8-10](), [nv-attestation-sdk-cpp/CMakeLists.txt:103-114](), [nv-attestation-cli/CMakeLists.txt:8]()

---

## Development Workflow

The typical development cycle follows this pattern:

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Repo as Local Repository
    participant Build as Build System
    participant Tests as Test Suite
    participant Format as Code Formatter
    participant Fork as GitHub Fork
    participant Upstream as Upstream Repo
    
    Dev->>Repo: Create issue-based branch
    
    loop Development Cycle
        Dev->>Repo: Implement changes
        Dev->>Build: cmake --build build
        
        alt Build Fails
            Build-->>Dev: Compilation errors
            Dev->>Dev: Fix errors
        else Build Succeeds
            Build-->>Dev: Artifacts ready
            Dev->>Tests: Run tests
            
            alt Tests Fail
                Tests-->>Dev: Test failures
                Dev->>Dev: Fix issues
            else Tests Pass
                Tests-->>Dev: All tests pass
            end
        end
    end
    
    Dev->>Format: git-clang-format --style file
    Format-->>Dev: Code formatted
    
    Dev->>Repo: git commit -s -m "message"
    Note over Dev,Repo: Sign-off required (DCO)
    
    Dev->>Fork: git push origin branch
    Fork->>Upstream: Create Pull Request
    
    Upstream-->>Dev: Code review feedback
    
    alt Changes Requested
        Dev->>Repo: Address feedback
        Dev->>Fork: git push origin branch
    else Approved
        Upstream->>Upstream: Merge PR
    end
```

**Sources**: [CONTRIBUTING.md:76-140]()

### Commit Requirements

All commits must:
1. **Reference an issue**: Format as `#<Issue Number> - <Commit Title>`
2. **Be signed off**: Use `git commit -s` to add Developer Certificate of Origin
3. **Follow formatting**: Code must be formatted with `clang-format`
4. **Build cleanly**: No warnings or errors
5. **Pass tests**: All existing tests must continue passing

**Sources**: [CONTRIBUTING.md:47-52](), [CONTRIBUTING.md:99-113]()

---

## Testing Strategy Overview

The project includes multiple test levels with configurable execution modes:

### Test Infrastructure Components

| Component | Location | Purpose |
|-----------|----------|---------|
| SDK Unit Tests | `nv-attestation-sdk-cpp/unit-tests/` | Test individual SDK components |
| SDK Integration Tests | `nv-attestation-sdk-cpp/integration-tests/` | Test SDK end-to-end flows |
| CLI Tests | `nv-attestation-cli/tests/` | Test CLI application and subcommands |
| Test Evidence | `nv-attestation-cli/tests/data/` | Pre-recorded GPU and switch evidence |
| Test Policies | `nv-attestation-cli/tests/policies/` | Rego policies for testing |

### Test Environment Configuration

Tests can be configured via environment variables:

```mermaid
graph TD
    subgraph "Test Configuration"
        ENV["Environment Variables"]
        TEST_MODE["TEST_MODE<br/>unit or integration"]
        TEST_DEVICES["TEST_DEVICES<br/>Device indices to test"]
    end
    
    subgraph "Test Execution Modes"
        UNIT["Unit Mode<br/>Direct function calls<br/>Fast, no hardware"]
        INTEG["Integration Mode<br/>Full CLI execution<br/>Can use real hardware"]
    end
    
    subgraph "Test Data Sources"
        FILES["Pre-recorded Evidence<br/>hopper_evidence.json<br/>switch_evidence_ls10.json"]
        HARDWARE["Live Hardware<br/>Via NVML/NSCQ"]
    end
    
    ENV --> TEST_MODE
    ENV --> TEST_DEVICES
    
    TEST_MODE -->|"unit"| UNIT
    TEST_MODE -->|"integration"| INTEG
    
    UNIT --> FILES
    INTEG --> FILES
    INTEG --> HARDWARE
    
    TEST_DEVICES -.->|"Specifies indices"| HARDWARE
```

For detailed information on the testing infrastructure, see [Testing Infrastructure](#6.3).

**Sources**: Based on system diagrams provided and test architecture patterns

---

## Development Tools Reference

### Essential Commands

```bash
# Initial setup
cmake -B build -S . -DBUILD_TESTING=ON -DENABLE_NVML=ON

# Build
cmake --build build

# Run tests
cd build && ctest

# Format code
git-clang-format --style file

# Format specific files
clang-format -style=file -i -fallback-style=none src/attestation.cpp

# Build with sanitizer
cmake -B build -S . -DSANITIZER=address
cmake --build build

# Clean build
rm -rf build
cmake -B build -S .
```

**Sources**: [CONTRIBUTING.md:22-39]()

### CMake Configuration Examples

```bash
# Development build with all features
cmake -B build -S nv-attestation-cli \
  -DCMAKE_BUILD_TYPE=Debug \
  -DBUILD_TESTING=ON \
  -DENABLE_NVML=ON \
  -DENABLE_NSCQ=ON

# Release build for production
cmake -B build -S nv-attestation-cli \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=ON \
  -DENABLE_NVML=ON

# Testing with sanitizer
cmake -B build -S nv-attestation-sdk-cpp \
  -DBUILD_TESTING=ON \
  -DSANITIZER=thread \
  -DENABLE_NVML=OFF
```

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:12-17]()

---

## Module Organization

The codebase is organized into well-defined modules with clear boundaries:

```mermaid
graph TB
    subgraph "nv-attestation-sdk-cpp/src/"
        CORE["Core Module<br/>nvat.cpp<br/>attestation.cpp<br/>verify.cpp<br/>claims.cpp<br/>claims_evaluator.cpp"]
        
        GPU_MOD["GPU Module<br/>gpu/evidence.cpp<br/>gpu/claims.cpp<br/>gpu/verify.cpp<br/>gpu/nvml_client.cpp"]
        
        SWITCH_MOD["Switch Module<br/>switch/evidence.cpp<br/>switch/claims.cpp<br/>switch/verify.cpp<br/>switch/nscq_client.cpp"]
        
        SPDM_MOD["SPDM Module<br/>spdm/spdm_measurement_records.cpp<br/>spdm/spdm_req.cpp<br/>spdm/spdm_resp.cpp<br/>spdm/spdm_opaque_data_parser.cpp"]
        
        GPU_SPDM["GPU SPDM<br/>gpu/spdm/gpu_opaque_data_parser.cpp"]
        
        SWITCH_SPDM["Switch SPDM<br/>switch/spdm/switch_opaque_data_parser.cpp"]
        
        UTIL["Utilities<br/>init.cpp, log.cpp<br/>nv_x509.cpp, nv_http.cpp<br/>nv_jwt.cpp, rim.cpp<br/>utils.cpp, error.cpp"]
        
        REGO["Policy Engine<br/>rego_engine/regorus_rego_engine.cpp"]
    end
    
    subgraph "nv-attestation-cli/src/"
        CLI_MAIN["CLI Entry<br/>main.cpp"]
        CLI_VER["Version Handler<br/>version.cpp"]
        CLI_ATT["Attest Handler<br/>attest.cpp"]
    end
    
    CORE --> GPU_MOD
    CORE --> SWITCH_MOD
    CORE --> REGO
    CORE --> UTIL
    
    GPU_MOD --> SPDM_MOD
    GPU_MOD --> GPU_SPDM
    
    SWITCH_MOD --> SPDM_MOD
    SWITCH_MOD --> SWITCH_SPDM
    
    CORE --> CLI_ATT
    CLI_MAIN --> CLI_VER
    CLI_MAIN --> CLI_ATT
```

For detailed code organization information, see [Code Organization](#6.2).

**Sources**: [nv-attestation-sdk-cpp/CMakeLists.txt:123-152](), [nv-attestation-cli/CMakeLists.txt:27-31]()

---

## Next Steps

For more detailed information on specific development topics:

- **[Building from Source](#6.1)**: Detailed build instructions, dependency installation, and build options
- **[Code Organization](#6.2)**: Source file structure, module boundaries, and architectural patterns  
- **[Testing Infrastructure](#6.3)**: Test framework details, test modes, and how to run tests
- **[Code Quality Standards](#6.4)**: clang-tidy configuration, code review criteria, and quality gates
- **[Resource Management Patterns](#6.5)**: C++ patterns used in the SDK for safe resource handling

For contribution guidelines and community standards:

- **[Contributing](#7)**: Complete contribution workflow and requirements
- **[Code of Conduct](#7.2)**: Community behavioral expectations
- **[Security Policy](#7.3)**: How to report security vulnerabilities

---

