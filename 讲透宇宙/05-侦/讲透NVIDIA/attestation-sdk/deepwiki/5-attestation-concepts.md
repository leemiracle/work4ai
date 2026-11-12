<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/attestation-sdk · page 5 Attestation Concepts · fetched 2026-10-26 -->

# Attestation Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [common-test-data/serialized_test_evidence/hopper_evidence.json](common-test-data/serialized_test_evidence/hopper_evidence.json)
- [nv-attestation-cli/src/attest.cpp](nv-attestation-cli/src/attest.cpp)

</details>



## Purpose and Scope

This page introduces the fundamental attestation concepts implemented in the NVIDIA Attestation SDK. It covers the core components involved in attestation—evidence collection, claims generation, policy evaluation, and verification—and explains how these concepts are realized in the codebase.

For detailed information about specific aspects of attestation:
- For the complete attestation workflow and step-by-step process, see [Device Attestation Flow](#5.1)
- For detailed evidence structure and serialization formats, see [Evidence Format and Structure](#5.2)
- For policy authoring and evaluation, see [Relying Party Policies](#5.3)
- For choosing between local and remote verification, see [Verification Modes](#5.4)
- For hardware-specific considerations, see [Device Support](#5.5)

For architectural information about the SDK implementation, see [Core SDK](#3.2).

---

## What is Attestation?

**Attestation** is the process of verifying that a device or computing environment is in a trusted state. In the context of NVIDIA's Confidential Computing solutions, attestation provides cryptographic proof that:

1. **Hardware identity** - The device is a genuine NVIDIA product
2. **Firmware integrity** - The firmware and software running on the device match expected reference measurements
3. **Configuration state** - The device is configured according to security policies

The NVIDIA Attestation SDK implements a complete attestation system that collects evidence from NVIDIA GPUs and NVSwitch devices, verifies this evidence against reference measurements, evaluates security policies, and produces structured attestation results.

**Sources:** [README.md:1-20]()

---

## Core Attestation Components

The attestation system consists of four primary components that work together to establish trust:

```mermaid
graph TB
    subgraph "Attestation Components"
        EVIDENCE["Evidence<br/>(SPDM measurements,<br/>certificates, metadata)"]
        CLAIMS["Claims<br/>(nvat_claims_collection_t)"]
        POLICY["Relying Party Policy<br/>(nvat_relying_party_policy_t)"]
        VERIFIER["Verifier<br/>(NVAT_VERIFY_LOCAL or<br/>NVAT_VERIFY_REMOTE)"]
    end
    
    subgraph "SDK Entry Point"
        ATTEST["nvat_attest_device()"]
    end
    
    subgraph "Configuration"
        CTX["nvat_attestation_ctx_t<br/>(Attestation Context)"]
    end
    
    subgraph "External Services"
        RIM["RIM Store<br/>(nvat_rim_store_t)<br/>Reference measurements"]
        OCSP["OCSP Client<br/>(nvat_ocsp_client_t)<br/>Certificate validation"]
        NRAS["NRAS<br/>(Remote attestation service)"]
    end
    
    CTX -->|"configures"| ATTEST
    EVIDENCE -->|"input"| ATTEST
    POLICY -->|"configured in"| CTX
    VERIFIER -->|"configured in"| CTX
    
    ATTEST -->|"produces"| CLAIMS
    ATTEST -->|"uses (if remote)"| RIM
    ATTEST -->|"uses (if remote)"| OCSP
    ATTEST -->|"uses (if remote)"| NRAS
```

**Sources:** [nv-attestation-cli/src/attest.cpp:196-334]()

### Evidence

**Evidence** is the raw cryptographic and measurement data collected from a device. It consists of:

- **SPDM measurement records** - Secure measurements of firmware and configuration
- **Certificate chains** - X.509 certificates establishing device identity
- **Opaque data** - Architecture-specific binary data
- **Metadata** - Driver version, VBIOS version, architecture type, nonce

Evidence can be collected from two sources:
1. **Live collection** - Queried directly from hardware via NVML (GPU) or NSCQ (Switch)
2. **Pre-serialized files** - Loaded from JSON files for testing or offline verification

The SDK represents evidence internally and processes it through device-specific verification logic in [nv-attestation-sdk-cpp/src/gpu/verify.cpp]() and [nv-attestation-sdk-cpp/src/switch/verify.cpp]().

**Sources:** [common-test-data/serialized_test_evidence/hopper_evidence.json:1](), [nv-attestation-cli/src/attest.cpp:216-228]()

### Claims

**Claims** are structured attestation results produced after verification. They represent verified facts about the device state. The SDK generates claims in the form of an `nvat_claims_collection_t` object, which contains:

- **Device identity claims** - UUID, architecture, firmware versions
- **Verification results** - Pass/fail status for measurements, certificates, policies
- **Measurement claims** - Individual SPDM measurement results
- **Overall attestation result** - Combined pass/fail determination

Claims are serialized to JSON for output and can be further wrapped in Entity Attestation Tokens (EAT) for standardized attestation reporting.

**Sources:** [nv-attestation-cli/src/attest.cpp:286-318]()

### Relying Party Policy

A **Relying Party Policy** defines the security requirements that the relying party (the entity trusting the attestation result) requires. Policies are written in **Rego** (the policy language from Open Policy Agent) and evaluate claims to determine if they meet requirements.

The SDK uses `nvat_relying_party_policy_t` objects created from Rego strings:

```cpp
nvat_relying_party_policy_create_rego_from_str(&rp_raw, rego_str.c_str());
```

Policies can check:
- Device type and architecture
- Specific firmware versions
- Certificate validity
- Individual measurement values
- Any combination of claims

**Sources:** [nv-attestation-cli/src/attest.cpp:115-146]()

### Verifier

The **Verifier** performs the cryptographic and logical verification of evidence. The SDK supports two verifier types configured via `NVAT_VERIFY_LOCAL` or `NVAT_VERIFY_REMOTE`:

| Verifier Type | Description | When to Use |
|---------------|-------------|-------------|
| `NVAT_VERIFY_LOCAL` | Performs all verification locally within the SDK | Environments with pre-cached RIM data, air-gapped systems, or when minimizing external dependencies |
| `NVAT_VERIFY_REMOTE` | Delegates verification to NVIDIA Remote Attestation Service (NRAS) | Production environments with internet access, when trusting NVIDIA's verification service |

Local verification requires configuring RIM stores and OCSP clients. Remote verification delegates to NRAS but still performs local policy evaluation.

**Sources:** [nv-attestation-cli/src/attest.cpp:272-284]()

---

## Attestation Context Configuration

The `nvat_attestation_ctx_t` object is the primary configuration interface for attestation operations. It encapsulates all parameters needed to perform attestation:

```mermaid
graph LR
    subgraph "Configuration Functions"
        F1["nvat_attestation_ctx_create()"]
        F2["nvat_attestation_ctx_set_device_type()"]
        F3["nvat_attestation_ctx_set_verifier_type()"]
        F4["nvat_attestation_ctx_set_relying_party_policy()"]
        F5["nvat_attestation_ctx_set_default_rim_store()"]
        F6["nvat_attestation_ctx_set_default_ocsp_client()"]
        F7["nvat_attestation_ctx_set_gpu_evidence_source_json_file()"]
        F8["nvat_attestation_ctx_set_switch_evidence_source_json_file()"]
    end
    
    subgraph "Context Object"
        CTX["nvat_attestation_ctx_t"]
    end
    
    subgraph "Attestation Execution"
        ATTEST["nvat_attest_device(ctx, nonce, eat, claims)"]
    end
    
    F1 -->|"creates"| CTX
    F2 -->|"NVAT_DEVICE_GPU or<br/>NVAT_DEVICE_NVSWITCH"| CTX
    F3 -->|"NVAT_VERIFY_LOCAL or<br/>NVAT_VERIFY_REMOTE"| CTX
    F4 -->|"nvat_relying_party_policy_t"| CTX
    F5 -->|"nvat_rim_store_t"| CTX
    F6 -->|"nvat_ocsp_client_t"| CTX
    F7 -->|"file path"| CTX
    F8 -->|"file path"| CTX
    
    CTX --> ATTEST
```

**Configuration Steps:**

1. **Create context** - Initialize with `nvat_attestation_ctx_create()`
2. **Set device type** - Specify GPU or NVSwitch target
3. **Configure evidence source** - Live collection (default) or file-based
4. **Set verifier type** - Local or remote verification
5. **Configure services** - RIM store, OCSP client for local verification
6. **Set policy** - Relying party policy for evaluation
7. **Execute attestation** - Call `nvat_attest_device()`

**Sources:** [nv-attestation-cli/src/attest.cpp:198-284]()

---

## Attestation Execution Flow

The complete attestation flow from invocation to result output:

```mermaid
sequenceDiagram
    participant CLI as "nvattest CLI"
    participant CTX as "nvat_attestation_ctx_t"
    participant SDK as "nvat_attest_device()"
    participant DEV as "Device<br/>(NVML/NSCQ)"
    participant VER as "Verifier"
    participant POL as "Policy Engine"
    
    CLI->>CTX: nvat_attestation_ctx_create()
    CLI->>CTX: Set configuration<br/>(device, verifier, policy, services)
    CLI->>SDK: nvat_attest_device(ctx, nonce, &eat, &claims)
    
    SDK->>DEV: Collect evidence
    DEV-->>SDK: Evidence (certificates,<br/>measurements, metadata)
    
    SDK->>VER: Verify evidence
    Note over VER: - Check certificates<br/>- Validate measurements<br/>- Compare against RIMs
    VER-->>SDK: Verification results
    
    SDK->>POL: Evaluate policy
    Note over POL: Run Rego policy<br/>against claims
    POL-->>SDK: Policy result
    
    SDK-->>CLI: nvat_claims_collection_t<br/>+ detached EAT
    CLI->>CLI: nvat_claims_collection_serialize_json()
    CLI->>CLI: Output JSON
```

**Key Function Calls:**

- **[nv-attestation-cli/src/attest.cpp:296]()** - `nvat_attest_device(ctx, nonce_ptr, &detached_eat, &raw_claims)`
- **[nv-attestation-cli/src/attest.cpp:315]()** - `nvat_claims_collection_serialize_json(claims, &serialized_claims)`

**Sources:** [nv-attestation-cli/src/attest.cpp:149-334]()

---

## Device Types and Architectures

The SDK supports attestation for two device types, each with architecture-specific handling:

| Device Type | Enum Constant | Evidence Collection | Architecture Support |
|-------------|---------------|---------------------|---------------------|
| GPU | `NVAT_DEVICE_GPU` | NVML library | HOPPER, future architectures |
| NVSwitch | `NVAT_DEVICE_NVSWITCH` | NSCQ library | LS10, future switches |

**Architecture-Specific Fields:**

The evidence structure includes an `arch` field that identifies the hardware architecture (e.g., `"HOPPER"` for H100 GPUs). Architecture-specific verification logic processes opaque data fields that contain measurement records in SPDM format.

**Example from evidence:**
```json
{
  "arch": "HOPPER",
  "driver_version": "550.90.07",
  "vbios_version": "96.00.9F.00.01"
}
```

**Sources:** [common-test-data/serialized_test_evidence/hopper_evidence.json:1](), [nv-attestation-cli/src/attest.cpp:204-214]()

---

## Result Codes and Output

Attestation operations return one of several result codes indicating the outcome:

| Result Code | Constant | Meaning |
|-------------|----------|---------|
| Success | `NVAT_RC_OK` | Attestation passed all checks |
| Policy mismatch | `NVAT_RC_RP_POLICY_MISMATCH` | Policy evaluation failed |
| Overall failure | `NVAT_RC_OVERALL_RESULT_FALSE` | Verification failed |
| Bad argument | `NVAT_RC_BAD_ARGUMENT` | Invalid input parameters |
| Internal error | `NVAT_RC_INTERNAL_ERROR` | SDK internal error |

**Output Structure:**

The CLI produces JSON output with the following structure:

```json
{
  "result_code": 0,
  "result_message": "Success",
  "claims": { /* claims object */ },
  "detached_eat": { /* EAT token */ }
}
```

Even when attestation fails (policy mismatch or overall result false), claims and EAT are still populated so that the relying party can inspect what failed.

**Sources:** [nv-attestation-cli/src/attest.cpp:36-68](), [nv-attestation-cli/src/attest.cpp:296-309]()

---

## SDK Initialization and Lifecycle

Before performing attestation, the SDK must be initialized. The lifecycle management follows this pattern:

```mermaid
graph TB
    subgraph "Initialization Phase"
        OPTS["nvat_sdk_opts_create()"]
        LOGGER["nvat_logger_spdlog_create()"]
        SET_LOGGER["nvat_sdk_opts_set_logger()"]
        INIT["nvat_sdk_init(opts)"]
    end
    
    subgraph "Attestation Phase"
        CTX_CREATE["nvat_attestation_ctx_create()"]
        CONFIG["Configure context<br/>(device, verifier, policy, etc.)"]
        ATTEST["nvat_attest_device()"]
    end
    
    subgraph "Cleanup Phase"
        SHUTDOWN["nvat_sdk_shutdown()"]
    end
    
    OPTS --> SET_LOGGER
    LOGGER --> SET_LOGGER
    SET_LOGGER --> INIT
    INIT --> CTX_CREATE
    CTX_CREATE --> CONFIG
    CONFIG --> ATTEST
    ATTEST --> SHUTDOWN
```

**Logger Configuration:**

The SDK uses spdlog for logging and supports configurable log levels:

```cpp
nvat_log_level_t levels = {
    NVAT_LOG_LEVEL_TRACE,
    NVAT_LOG_LEVEL_DEBUG,
    NVAT_LOG_LEVEL_INFO,
    NVAT_LOG_LEVEL_WARN,
    NVAT_LOG_LEVEL_ERROR,
    NVAT_LOG_LEVEL_OFF
};
```

**Sources:** [nv-attestation-cli/src/attest.cpp:164-196](), [nv-attestation-cli/src/attest.cpp:352]()

---

## Resource Management

The SDK uses C APIs with explicit resource management. The CLI wraps SDK handles in `nv_unique_ptr` smart pointers for automatic cleanup:

```cpp
nv_unique_ptr<nvat_attestation_ctx_t> ctx;
nvat_attestation_ctx_t raw_ctx = nullptr;
nvat_attestation_ctx_create(&raw_ctx);
ctx.reset(&raw_ctx);  // Automatic cleanup on scope exit
```

**Key SDK Types Requiring Management:**

- `nvat_sdk_opts_t` - SDK initialization options
- `nvat_attestation_ctx_t` - Attestation context
- `nvat_claims_collection_t` - Claims output
- `nvat_relying_party_policy_t` - Policy object
- `nvat_rim_store_t` - RIM store handle
- `nvat_ocsp_client_t` - OCSP client handle
- `nvat_str_t` - String data from SDK

For details on resource management patterns, see [Resource Management Patterns](#6.5).

**Sources:** [nv-attestation-cli/src/attest.cpp:164-170](), [nv-attestation-cli/src/attest.cpp:198-202]()

---

## Nonce Handling

A **nonce** (number used once) is a cryptographic value that ensures attestation freshness and prevents replay attacks. The SDK supports:

1. **Auto-generated nonce** - SDK generates a random nonce if not provided
2. **User-provided nonce** - Pass hex-encoded nonce via `nvat_nonce_from_hex()`

```cpp
nvat_nonce_t nonce_ptr = nullptr;
if (!nonce.empty()) {
    nvat_nonce_from_hex(&nonce_ptr, nonce.c_str());
}
nvat_attest_device(ctx, nonce_ptr, &eat, &claims);
```

The nonce is included in the evidence and bound cryptographically to the attestation result, allowing the relying party to verify that the attestation is fresh and not replayed from a previous session.

**Sources:** [nv-attestation-cli/src/attest.cpp:289-295]()

---

## Service Endpoints Configuration

For local verification, the SDK requires access to external services:

| Service | Type | Purpose | Default URL |
|---------|------|---------|-------------|
| RIM Service | `nvat_rim_store_t` | Reference Integrity Manifests | `https://rim.attestation.nvidia.com` |
| OCSP Responder | `nvat_ocsp_client_t` | Certificate revocation status | `https://ocsp.ndis.nvidia.com` |
| NRAS | Environment variable | Remote attestation service | `https://nras.attestation.nvidia.com` |

**Configuration Example:**

```cpp
// RIM Store
nvat_rim_store_create_remote(&rim_store_raw, rim_base_url, nullptr);
nvat_attestation_ctx_set_default_rim_store(ctx, rim_store);

// OCSP Client
nvat_ocsp_client_create_default(&ocsp_client_raw, ocsp_base_url, nullptr);
nvat_attestation_ctx_set_default_ocsp_client(ctx, ocsp_client);

// NRAS (for remote verifier)
setenv("NVAT_NRAS_BASE_URL", nras_base_url, 1);
```

**Sources:** [nv-attestation-cli/src/attest.cpp:231-265]()

---

## Summary

The NVIDIA Attestation SDK implements a comprehensive attestation system built around four core concepts:

1. **Evidence** - Cryptographic measurements and certificates from devices
2. **Verification** - Validation of evidence against reference measurements and policies
3. **Claims** - Structured results representing verified facts
4. **Policies** - Rego-based security requirements evaluation

These components are orchestrated through the `nvat_attestation_ctx_t` configuration object and executed via `nvat_attest_device()`, producing JSON-serialized claims and EAT tokens that relying parties can use to establish trust in device state.

For implementation details on each concept, refer to the child pages listed at the beginning of this document.

---

