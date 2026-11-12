<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/attestation-sdk · page 4 Using the CLI · fetched 2026-10-26 -->

# Using the CLI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nv-attestation-cli/config.toml](nv-attestation-cli/config.toml)
- [nv-attestation-cli/src/attest.cpp](nv-attestation-cli/src/attest.cpp)
- [nv-attestation-cli/src/main.cpp](nv-attestation-cli/src/main.cpp)

</details>



## Purpose and Scope

This document provides a comprehensive guide to the `nvattest` command-line interface tool. The CLI wraps the NVIDIA Attestation SDK (nv-attestation-sdk-cpp) to provide device attestation functionality through a simple command-line interface. This page covers the overall CLI structure, invocation patterns, and configuration mechanisms.

For detailed information about specific topics, see:
- Command structure and available subcommands: [CLI Command Structure](#4.1)
- Complete attest subcommand documentation: [Attest Command Reference](#4.2)
- Configuration file format and options: [Configuration Files](#4.3)
- JSON output structure and result codes: [Output Format](#4.4)
- Core attestation concepts: [Attestation Concepts](#5)

## CLI Overview

The `nvattest` tool is a C++ application that provides a command-line interface for device attestation operations. It supports attestation of NVIDIA GPUs and switches through two primary subcommands:
- `attest` - Performs device attestation and returns structured results
- `version` - Displays version information

The CLI is built using the CLI11 library and integrates directly with the nvat SDK through C API bindings defined in `nvat.h`.

Sources: [nv-attestation-cli/src/main.cpp:29-58]()

## CLI Application Structure

The following diagram shows how the CLI application is structured and how command-line arguments flow through the system to SDK calls:

```mermaid
graph TD
    User["User invokes nvattest"]
    Main["main()<br/>main.cpp:29"]
    CLIApp["CLI::App<br/>'NVIDIA attestation CLI'<br/>main.cpp:35"]
    Config["Config File Parser<br/>--config flag<br/>config.toml"]
    
    subgraph "Subcommand Registration"
        CreateVersion["create_version_subcommand()<br/>version.cpp"]
        CreateAttest["create_attest_subcommand()<br/>attest.cpp:70"]
        VersionSub["version_subcommand<br/>CLI::App*"]
        AttestSub["attest_subcommand<br/>CLI::App*"]
    end
    
    subgraph "Argument Parsing"
        Parse["CLI11_PARSE(app, argc, argv)<br/>main.cpp:45"]
        Options["Parsed Options<br/>nonce, device, verifier, etc."]
    end
    
    subgraph "Subcommand Dispatch"
        CheckVersion["version_subcommand->parsed()?<br/>main.cpp:48"]
        CheckAttest["attest_subcommand->parsed()?<br/>main.cpp:50"]
        HandleVersion["handle_version_subcommand()"]
        HandleAttest["handle_attest_subcommand()<br/>attest.cpp:339"]
    end
    
    subgraph "SDK Integration"
        AttestFunc["attest()<br/>attest.cpp:149"]
        SDKInit["nvat_sdk_init()<br/>attest.cpp:193"]
        CtxCreate["nvat_attestation_ctx_create()<br/>attest.cpp:200"]
        DeviceAttest["nvat_attest_device()<br/>attest.cpp:296"]
        Output["AttestOutput::to_json()<br/>attest.cpp:36"]
    end
    
    User --> Main
    Main --> CLIApp
    CLIApp --> Config
    CLIApp --> CreateVersion
    CLIApp --> CreateAttest
    CreateVersion --> VersionSub
    CreateAttest --> AttestSub
    
    CLIApp --> Parse
    Config --> Parse
    Parse --> Options
    
    Options --> CheckVersion
    Options --> CheckAttest
    
    CheckVersion -->|true| HandleVersion
    CheckAttest -->|true| HandleAttest
    
    HandleAttest --> AttestFunc
    AttestFunc --> SDKInit
    AttestFunc --> CtxCreate
    AttestFunc --> DeviceAttest
    AttestFunc --> Output
    
    Output --> User
```

**CLI Application Flow from Entry Point to SDK**

The application initializes a `CLI::App` instance with configuration file support, registers subcommands through factory functions (`create_version_subcommand`, `create_attest_subcommand`), parses arguments using `CLI11_PARSE`, dispatches to the appropriate handler function, and returns JSON-formatted results.

Sources: [nv-attestation-cli/src/main.cpp:29-58](), [nv-attestation-cli/src/attest.cpp:70-106](), [nv-attestation-cli/src/attest.cpp:339-357]()

## Command Invocation

The basic invocation pattern for `nvattest` follows standard CLI conventions:

```
nvattest [global-options] <subcommand> [subcommand-options]
```

### Global Options

The CLI supports one global option that applies across all subcommands:

| Option | Description | Default |
|--------|-------------|---------|
| `--config <file>` | Path to TOML configuration file | `config.toml` |

Sources: [nv-attestation-cli/src/main.cpp:36]()

### Subcommands

| Subcommand | Purpose | Handler Function |
|------------|---------|------------------|
| `attest` | Run device attestation | `handle_attest_subcommand()` |
| `version` | Display version information | `handle_version_subcommand()` |

When invoked without a subcommand, the CLI displays help information.

Sources: [nv-attestation-cli/src/main.cpp:42-55]()

## Configuration Precedence

The CLI uses a layered configuration system where options can be specified in multiple locations. The precedence order (highest to lowest) is:

1. **Command-line arguments** - Explicitly provided via flags
2. **Configuration file** - Values from `config.toml` or custom config file
3. **Default values** - Built-in defaults from subcommand definitions

The following diagram illustrates how configuration values are resolved:

```mermaid
flowchart TD
    Start["Configuration Resolution<br/>for attest subcommand"]
    
    subgraph "Configuration Sources"
        CLI["Command-line Arguments<br/>--device, --verifier, etc."]
        TOML["config.toml [attest] section<br/>device = 'gpu'<br/>verifier = 'local'"]
        Defaults["Default Values<br/>create_attest_subcommand()<br/>->default_val()"]
    end
    
    subgraph "Resolution Process"
        Check1{"CLI arg<br/>provided?"}
        Check2{"TOML value<br/>exists?"}
        UseCLI["Use CLI value"]
        UseTOML["Use TOML value"]
        UseDefault["Use default value"]
    end
    
    subgraph "Parameter Variables"
        DeviceVar["device: std::string"]
        VerifierVar["verifier: std::string"]
        EvidenceVar["gpu_evidence: std::string"]
        PolicyVar["relying_party_policy: std::string"]
        OtherVars["nonce, rim_url, ocsp_url,<br/>nras_url, log_level"]
    end
    
    Start --> CLI
    Start --> TOML
    Start --> Defaults
    
    CLI --> Check1
    TOML --> Check1
    Defaults --> Check1
    
    Check1 -->|Yes| UseCLI
    Check1 -->|No| Check2
    Check2 -->|Yes| UseTOML
    Check2 -->|No| UseDefault
    
    UseCLI --> DeviceVar
    UseTOML --> DeviceVar
    UseDefault --> DeviceVar
    
    DeviceVar --> VerifierVar
    VerifierVar --> EvidenceVar
    EvidenceVar --> PolicyVar
    PolicyVar --> OtherVars
```

**Configuration Value Resolution Process**

The CLI11 library handles configuration precedence automatically. When `CLI11_PARSE` is invoked, it first reads the configuration file (if specified), then processes command-line arguments which override config file values.

Sources: [nv-attestation-cli/src/main.cpp:36-45](), [nv-attestation-cli/src/attest.cpp:70-106](), [nv-attestation-cli/config.toml:1-13]()

## Basic Usage Examples

### Attest a GPU (Local Verification)

```bash
nvattest attest --device gpu --verifier local
```

This invokes `handle_attest_subcommand()` which creates an attestation context, sets device type to `NVAT_DEVICE_GPU`, configures local verification, and calls `nvat_attest_device()`.

### Attest a GPU with Custom Policy

```bash
nvattest attest --device gpu --verifier local \
  --relying-party-policy /path/to/policy.rego
```

The policy file is loaded in `set_relying_party_policy()` at [attest.cpp:115-146]() and applied via `nvat_attestation_ctx_set_relying_party_policy()`.

### Attest Using Pre-Collected Evidence

```bash
nvattest attest --device gpu --verifier local \
  --gpu-evidence /path/to/evidence.json
```

This uses file-based evidence instead of querying hardware. The evidence source is configured via `nvat_attestation_ctx_set_gpu_evidence_source_json_file()` at [attest.cpp:217-221]().

### Remote Verification with Custom Endpoints

```bash
nvattest attest --device nvswitch --verifier remote \
  --rim-url https://custom-rim.example.com \
  --ocsp-url https://custom-ocsp.example.com \
  --nras-url https://custom-nras.example.com
```

Service URLs are configured through SDK functions `nvat_rim_store_create_remote()`, `nvat_ocsp_client_create_default()`, and environment variable `NVAT_NRAS_BASE_URL` at [attest.cpp:231-265]().

### Using Configuration File

```bash
nvattest --config /path/to/custom-config.toml attest
```

The configuration file follows TOML format with sections corresponding to subcommands. See [Configuration Files](#4.3) for format details.

Sources: [nv-attestation-cli/src/attest.cpp:149-357]()

## SDK Integration Pattern

The CLI's integration with the SDK follows a consistent pattern for all operations:

```mermaid
sequenceDiagram
    participant CLI as handle_attest_subcommand
    participant Attest as attest()
    participant SDK as NVAT SDK Functions
    participant Wrappers as nv_unique_ptr Wrappers
    
    CLI->>Attest: Call with parsed arguments
    
    Note over Attest: Create SDK options
    Attest->>SDK: nvat_sdk_opts_create(&raw_opts)
    Attest->>Wrappers: opts.reset(&raw_opts)
    
    Note over Attest: Configure logger
    Attest->>SDK: nvat_logger_spdlog_create(&logger, level)
    Attest->>SDK: nvat_sdk_opts_set_logger(*opts, logger)
    
    Note over Attest: Initialize SDK
    Attest->>SDK: nvat_sdk_init(*opts)
    
    Note over Attest: Create attestation context
    Attest->>SDK: nvat_attestation_ctx_create(&raw_ctx)
    Attest->>Wrappers: ctx.reset(&raw_ctx)
    
    Note over Attest: Configure context
    Attest->>SDK: nvat_attestation_ctx_set_device_type(*ctx, type)
    Attest->>SDK: nvat_attestation_ctx_set_verifier_type(*ctx, type)
    Attest->>SDK: nvat_attestation_ctx_set_*_evidence_source_*()
    Attest->>SDK: nvat_attestation_ctx_set_relying_party_policy()
    
    Note over Attest: Perform attestation
    Attest->>SDK: nvat_attest_device(*ctx, nonce, &eat, &claims)
    SDK-->>Attest: nvat_rc_t result code
    
    Note over Attest: Serialize results
    Attest->>SDK: nvat_claims_collection_serialize_json(*claims, &json)
    Attest->>SDK: nvat_str_get_data(claims, &data)
    Attest->>SDK: nvat_str_get_data(detached_eat, &data)
    
    Attest-->>CLI: AttestOutput(result_code, claims, eat)
    
    CLI->>SDK: nvat_sdk_shutdown()
    CLI->>CLI: AttestOutput::to_json()
    CLI-->>CLI: Print JSON to stdout
    CLI-->>CLI: Return result_code
```

**SDK Function Call Pattern**

The `attest()` function demonstrates the standard pattern for SDK integration: create options, initialize SDK, create context, configure context parameters, execute operation, retrieve results, and shutdown. The `nv_unique_ptr` wrapper (defined in SDK headers) provides RAII-based resource management for SDK objects.

Sources: [nv-attestation-cli/src/attest.cpp:149-357]()

## Return Codes and Error Handling

The CLI returns exit codes that correspond to `nvat_rc_t` values from the SDK. The primary result codes are:

| Exit Code | Name | Meaning |
|-----------|------|---------|
| 0 | `NVAT_RC_OK` | Attestation succeeded |
| Non-zero | Various error codes | Attestation failed or error occurred |

When errors occur during attestation, the `attest()` function returns an `AttestOutput` object containing the error code. This is converted to JSON and printed to stdout before the application exits with the error code.

The function handles three special cases that still produce output:
- `NVAT_RC_OK` - Success
- `NVAT_RC_RP_POLICY_MISMATCH` - Policy evaluation failed
- `NVAT_RC_OVERALL_RESULT_FALSE` - Overall attestation result is false

These cases return claims and EAT data even though attestation did not fully succeed. All other error codes return immediately without claims or EAT data.

Sources: [nv-attestation-cli/src/attest.cpp:30-68](), [nv-attestation-cli/src/attest.cpp:296-334](), [nv-attestation-cli/src/attest.cpp:339-357]()

## Logging and Diagnostics

The CLI supports configurable logging through the `--log-level` option. Log levels map to `nvat_log_level_t` values:

| CLI Value | SDK Constant | Description |
|-----------|--------------|-------------|
| `trace` | `NVAT_LOG_LEVEL_TRACE` | Most verbose |
| `debug` | `NVAT_LOG_LEVEL_DEBUG` | Debug information |
| `info` | `NVAT_LOG_LEVEL_INFO` | Informational messages |
| `warn` | `NVAT_LOG_LEVEL_WARN` | Warnings (default) |
| `error` | `NVAT_LOG_LEVEL_ERROR` | Errors only |
| `off` | `NVAT_LOG_LEVEL_OFF` | No logging |

The logger is created via `nvat_logger_spdlog_create()` and attached to the SDK options before initialization. This enables diagnostic output from both CLI and SDK operations.

Sources: [nv-attestation-cli/src/attest.cpp:172-189](), [nv-attestation-cli/src/attest.cpp:102-104](), [nv-attestation-cli/src/main.cpp:30-33]()

## Configuration File Format

The CLI supports TOML configuration files for persistent option storage. The configuration file is organized into sections corresponding to subcommands:

```toml
# Global section for application-wide settings
[default]

# Version subcommand configuration
[version]

# Attest subcommand configuration  
[attest]
device = "gpu"
verifier = "local"
gpu-evidence = ""
switch-evidence = ""
relying-party-policy = ""
```

Each option in the `[attest]` section corresponds to a command-line flag. When both are present, command-line arguments take precedence.

Sources: [nv-attestation-cli/config.toml:1-13]()

## Next Steps

For more detailed information about using the CLI, see:
- [CLI Command Structure](#4.1) - Detailed command structure and argument parsing
- [Attest Command Reference](#4.2) - Complete reference for all attest options
- [Configuration Files](#4.3) - Full configuration file format specification
- [Output Format](#4.4) - Understanding JSON output structure and result codes

---

