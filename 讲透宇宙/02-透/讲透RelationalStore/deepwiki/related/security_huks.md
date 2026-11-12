> 来源: [https://deepwiki.com/openharmony/security_huks](https://deepwiki.com/openharmony/security_huks)
> DeepWiki openharmony/security_huks

# Overview

  Relevant source files 
 - [BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/BUILD.gn)
 - [build/config.gni](https://github.com/openharmony/security_huks/blob/e99d2312/build/config.gni)
 - [bundle.json](https://github.com/openharmony/security_huks/blob/e99d2312/bundle.json)
 - [frameworks/config/build/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/config/build/BUILD.gn)
 - [frameworks/huks_standard/main/common/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/common/BUILD.gn)
 - [frameworks/huks_standard/main/common/include/huks_service_ipc_interface_code.h](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/common/include/huks_service_ipc_interface_code.h)
 - [frameworks/huks_standard/main/core/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/core/BUILD.gn)
 - [frameworks/huks_standard/main/crypto_engine/mbedtls/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/crypto_engine/mbedtls/BUILD.gn)
 - [frameworks/huks_standard/main/crypto_engine/openssl/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/crypto_engine/openssl/BUILD.gn)
 - [frameworks/huks_standard/main/os_dependency/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/os_dependency/BUILD.gn)
 - [frameworks/huks_standard/main/os_dependency/ipc/include/hks_client_ipc.h](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/os_dependency/ipc/include/hks_client_ipc.h)
 - [frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_ipc.c](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_ipc.c)
 - [frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_passthrough.c](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_passthrough.c)
 - [huks.gni](https://github.com/openharmony/security_huks/blob/e99d2312/huks.gni)
 - [interfaces/inner_api/huks_lite/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_lite/BUILD.gn)
 - [interfaces/inner_api/huks_standard/main/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/BUILD.gn)
 - [interfaces/inner_api/huks_standard/main/include/hks_api.h](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/include/hks_api.h)
 - [interfaces/inner_api/huks_standard/main/include/hks_param.h](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/include/hks_param.h)
 - [interfaces/inner_api/huks_standard/main/libhukschipsetsdk.map](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/libhukschipsetsdk.map)
 - [interfaces/inner_api/huks_standard/main/libhukssdk.map](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/libhukssdk.map)
 - [interfaces/inner_api/huks_standard/source/hks_api.c](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c)
 - [services/huks_standard/huks_engine/main/core/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_engine/main/core/BUILD.gn)
 - [services/huks_standard/huks_service/main/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/BUILD.gn)
 - [services/huks_standard/huks_service/main/core/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/BUILD.gn)
 - [services/huks_standard/huks_service/main/core/include/hks_client_service.h](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/include/hks_client_service.h)
 - [services/huks_standard/huks_service/main/core/src/hks_client_service.c](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/src/hks_client_service.c)
 - [services/huks_standard/huks_service/main/os_dependency/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/BUILD.gn)
 - [services/huks_standard/huks_service/main/os_dependency/idl/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/BUILD.gn)
 - [services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.c](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.c)
 - [services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.h](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.h)
 - [services/huks_standard/huks_service/main/os_dependency/sa/hks_message_handler.h](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/sa/hks_message_handler.h)
 - [test/fuzz_test/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/test/fuzz_test/BUILD.gn)
 - [test/unittest/huks_lite_test/liteos_a_adapter/upgrade_test/version_one/module_test/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/test/unittest/huks_lite_test/liteos_a_adapter/upgrade_test/version_one/module_test/BUILD.gn)
 - [test/unittest/huks_standard_test/module_test/inner_kits_passthrough/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/test/unittest/huks_standard_test/module_test/inner_kits_passthrough/BUILD.gn)
 - [test/unittest/modify_old_version_key_test_util/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/test/unittest/modify_old_version_key_test_util/BUILD.gn)
 - [utils/crypto_adapter/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/utils/crypto_adapter/BUILD.gn)
 - [utils/file_operator/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/utils/file_operator/BUILD.gn)
 - [utils/mutex/BUILD.gn](https://github.com/openharmony/security_huks/blob/e99d2312/utils/mutex/BUILD.gn)
 
  
## Purpose

 This document provides an overview of the HUKS (OpenHarmony Universal KeyStore) repository, which implements a comprehensive hardware-backed key management and cryptographic services framework for OpenHarmony systems. HUKS provides secure key lifecycle management, cryptographic operations, and access control across different device profiles ranging from resource-constrained IoT devices to full-featured smartphones.

 For detailed architectural information, see [Architecture](https://deepwiki.com/openharmony/security_huks/2-architecture). For cryptographic operations, see [Core Operations](https://deepwiki.com/openharmony/security_huks/3-core-operations). For security mechanisms, see [Security Features](https://deepwiki.com/openharmony/security_huks/5-security-features). For external provider integration, see [UKey Extension System](https://deepwiki.com/openharmony/security_huks/6-ukey-extension-system).

 
## What is HUKS?

 HUKS is OpenHarmony's unified cryptographic framework that provides:

 
 - **Key Management**: Generation, storage, import, export, and deletion of cryptographic keys
 - **Cryptographic Operations**: Encryption, decryption, signing, verification, key agreement, and key derivation
 - **Access Control**: Authentication-based key usage with user verification (fingerprint, PIN, face)
 - **Hardware Integration**: Support for both software-based and hardware-backed (TEE/SE) cryptographic engines
 - **Provider Extension**: Plugin system for external cryptographic providers like hardware tokens (UKey)
 - **Multi-Level Deployment**: Adaptable architecture for standard, small, and mini OS environments
 
 The repository is located at `https://github.com/openharmony/security_huks` and is organized as a component within the OpenHarmony security subsystem.

 **Sources:** [bundle.json1-141](https://github.com/openharmony/security_huks/blob/e99d2312/bundle.json#L1-L141) [build/config.gni15-111](https://github.com/openharmony/security_huks/blob/e99d2312/build/config.gni#L15-L111)

 
## Repository Structure

 
```

```

 **Sources:** [bundle.json8-9](https://github.com/openharmony/security_huks/blob/e99d2312/bundle.json#L8-L9) [BUILD.gn1-130](https://github.com/openharmony/security_huks/blob/e99d2312/BUILD.gn#L1-L130)

 
## Key Components and Their Roles

 
| Component | Location | Purpose | Key Files |
|---|---|---|---|
| SDK API | interfaces/inner_api/huks_standard/main | Public API exposed to applications | hks_api.h, hks_api.c |
| Client IPC | frameworks/huks_standard/main/os_dependency/ipc | Client-side IPC communication | hks_client_service_ipc.c |
| Service Core | services/huks_standard/huks_service/main/core | Request validation and routing | hks_client_service.c |
| IPC Service | services/huks_standard/huks_service/main/os_dependency/idl/ipc | Server-side IPC handling | hks_ipc_service.c |
| Crypto Engine | services/huks_standard/huks_engine/main/core | Three-stage operation management | hks_core_service_three_stage.c |
| OpenSSL Backend | frameworks/huks_standard/main/crypto_engine/openssl | OpenSSL cryptographic implementation | hks_openssl_engine.c |
| MbedTLS Backend | frameworks/huks_standard/main/crypto_engine/mbedtls | MbedTLS cryptographic implementation | hks_mbedtls_engine.c |
| Storage Manager | services/huks_standard/huks_service/main/hks_storage | Key persistence with security levels | hks_storage_manager.c |
| Session Manager | services/huks_standard/huks_service/main/core | Three-stage session tracking | hks_session_manager.c |
| UKey Extension | services/huks_standard/huks_service/extension | External provider integration | ukey_client_service |

 **Sources:** [bundle.json97-139](https://github.com/openharmony/security_huks/blob/e99d2312/bundle.json#L97-L139) [services/huks_standard/huks_service/main/core/BUILD.gn1-243](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/BUILD.gn#L1-L243)

 
## Layered Architecture

 
```

```

 **Sources:** [interfaces/inner_api/huks_standard/source/hks_api.c1-700](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c#L1-L700) [services/huks_standard/huks_service/main/core/src/hks_client_service.c1-300](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/src/hks_client_service.c#L1-L300) [services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.c1-300](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_ipc_service.c#L1-L300)

 
## System Ability Integration

 HUKS operates as a System Ability (SA) with the following characteristics:

 
| Property | Value | Description |
|---|---|---|
| SA ID | 3510 | System Ability identifier for IPC |
| Service Name | huks_service | Registered name in SAMGR |
| Lifecycle | On-demand | Started on first client request |
| Communication | IPC (standard) / Passthrough (small/mini) | Architecture-dependent |
| Process Model | Independent process | Runs in dedicated huks_service process |

 **Sources:** [bundle.json18-26](https://github.com/openharmony/security_huks/blob/e99d2312/bundle.json#L18-L26) [services/huks_standard/huks_service/main/os_dependency/sa/hks_sa.cpp1-200](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/sa/hks_sa.cpp#L1-L200)

 
## Operation Patterns

 HUKS supports three primary operation patterns:

 
```

```

 
### One-Shot Operations

 Operations that complete in a single function call:

 
 - `HksGenerateKey` - Key generation
 - `HksEncrypt` / `HksDecrypt` - Small data encryption
 - `HksSign` / `HksVerify` - Digital signatures
 - `HksDeleteKey` - Key deletion
 
 **Sources:** [interfaces/inner_api/huks_standard/source/hks_api.c98-225](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c#L98-L225)

 
### Three-Stage Operations

 For streaming large data or operations requiring user authentication:

 
 - **Init** (`HksInit`) - Establishes session, returns handle and optional challenge token
 - **Update** (`HksUpdate`) - Processes data in chunks, can be called multiple times
 - **Finish** (`HksFinish`) - Completes operation and cleans up session
 
 **Sources:** [interfaces/inner_api/huks_standard/source/hks_api.c226-252](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c#L226-L252) [services/huks_standard/huks_service/main/core/src/hks_session_manager.c1-300](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/src/hks_session_manager.c#L1-L300)

 
### Extension Operations

 For external cryptographic providers (UKey system):

 
 - `HksRegisterProvider` - Register hardware token provider
 - `HksOpenRemoteHandle` - Open connection to external key
 - Three-stage operations through provider proxy
 
 **Sources:** [interfaces/inner_api/huks_standard/source/hks_api.c254-434](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c#L254-L434)

 
## Deployment Scenarios

 HUKS adapts to three OS levels with different feature sets:

 
| OS Level | Target Devices | Key Features | Build Output |
|---|---|---|---|
| standard | Smartphones, tablets | Full IPC, System Ability, multiple SDKs, UKey support | libhukssdk.so, libhukschipsetsdk.so, huks_service |
| small | IoT devices (128KB+ RAM) | IPC-based, reduced features | huks_sdk, huks_server |
| mini | Microcontrollers (<128KB RAM) | Minimal SDK, no service | huks_sdk (minimal) |

 **Configuration Source:** [build/config.gni15-111](https://github.com/openharmony/security_huks/blob/e99d2312/build/config.gni#L15-L111) [huks.gni1-50](https://github.com/openharmony/security_huks/blob/e99d2312/huks.gni#L1-L50)

 
### Standard System Architecture

 
```

```

 **Sources:** [BUILD.gn82-123](https://github.com/openharmony/security_huks/blob/e99d2312/BUILD.gn#L82-L123) [services/huks_standard/huks_engine/main/core/BUILD.gn25-96](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_engine/main/core/BUILD.gn#L25-L96)

 
### Small System Architecture

 
```

```

 **Sources:** [BUILD.gn94-103](https://github.com/openharmony/security_huks/blob/e99d2312/BUILD.gn#L94-L103) [services/huks_standard/huks_service/main/core/BUILD.gn166-241](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/BUILD.gn#L166-L241)

 
## Build Configuration

 Key build configuration flags control HUKS behavior:

 
| Flag | Default | Purpose |
|---|---|---|
| os_level | - | Determines system level: "standard", "small", or "mini" |
| huks_security_level | "software" | Crypto backend: "software" or "trusted_environment" |
| use_crypto_lib | "openssl" | Library choice: "openssl" or "mbedtls" |
| huks_enable_ukey_config | false | Enable UKey external provider support |
| huks_enable_hdi_in_standard | true | Enable HDI hardware interface on standard |
| huks_use_rkc_in_standard | false | Enable Root Key Component for key encryption |
| huks_enable_upgrade_key | true | Enable automatic key version upgrade |
| huks_key_store_standard_path | "/data/service/el1/public/huks_service" | Storage path on standard system |

 **Sources:** [build/config.gni15-111](https://github.com/openharmony/security_huks/blob/e99d2312/build/config.gni#L15-L111) [huks.gni14-50](https://github.com/openharmony/security_huks/blob/e99d2312/huks.gni#L14-L50)

 
## Data Flow Example: Key Generation

 
```

```

 **Sources:** [interfaces/inner_api/huks_standard/source/hks_api.c98-130](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/source/hks_api.c#L98-L130) [services/huks_standard/huks_service/main/core/src/hks_client_service.c607-665](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/src/hks_client_service.c#L607-L665) [frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_ipc.c558-590](https://github.com/openharmony/security_huks/blob/e99d2312/frameworks/huks_standard/main/os_dependency/ipc/src/hks_client_service_ipc.c#L558-L590)

 
## Key Data Structures

 
### HksBlob

 Basic binary data container used throughout HUKS:

 
```

```

 **Source:** Defined in `hks_type.h`

 
### HksParamSet

 Parameter container for passing configuration to HUKS operations:

 
```

```

 **Source:** Defined in `hks_type.h`, built via `hks_param.c`

 
### HksProcessInfo

 Identifies the calling process for access control:

 
```

```

 **Source:** [services/huks_standard/huks_service/main/core/include/hks_client_service.h1-155](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/core/include/hks_client_service.h#L1-L155)

 
## Extension Points

 HUKS provides several extension mechanisms:

 
### 1. UKey External Providers

 Register external cryptographic providers for hardware tokens:

 
 - **Registration:** `HksRegisterProvider(name, paramSet)`
 - **Remote Handles:** `HksOpenRemoteHandle(resourceId, paramSet)`
 - **Operations:** Three-stage operations proxied to external provider
 - **Plugin Loading:** Dynamic `.so` loading via `dlopen`
 
 **For details, see [UKey Extension System](https://deepwiki.com/openharmony/security_huks/6-ukey-extension-system)**

 
### 2. HDI Hardware Interface

 Hardware Driver Interface for TEE/SE integration:

 
 - Interface defined in `drivers_interface_huks`
 - Version 1.1 adapter: [services/huks_standard/huks_service/main/os_dependency/idl/passthrough/huks_hdi_v1_1_adapter.cpp](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/passthrough/huks_hdi_v1_1_adapter.cpp)
 
 
### 3. Plugin Adapters

 Service-level plugin hooks:

 
 - [services/huks_standard/huks_service/main/plugin_proxy/src/hks_plugin_adapter.cpp](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/plugin_proxy/src/hks_plugin_adapter.cpp)
 
 **Sources:** [services/huks_standard/huks_service/main/os_dependency/idl/BUILD.gn1-149](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/BUILD.gn#L1-L149)

 
## Security Architecture

 HUKS implements multiple layers of security:

 
| Security Layer | Mechanism | Implementation |
|---|---|---|
| Access Control | Permission checks, UID validation | hks_permission_check.cpp |
| Authorization | Parameter matching against key policy | hks_auth.c |
| User Authentication | Challenge-response with UserIAM | hks_useridm_api_wrap.cpp |
| Storage Encryption | Root Key Component (RKC) encryption | hks_rkc.c |
| Storage Levels | DE (Device Encrypted), CE (Credential Encrypted), ECE (Enhanced CE) | hks_storage_manager.c |
| Session Management | Handle limits, timeout, eviction | hks_session_manager.c |

 **For details, see [Security Features](https://deepwiki.com/openharmony/security_huks/5-security-features)**

 **Sources:** [services/huks_standard/huks_engine/main/core/src/hks_auth.c1-200](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_engine/main/core/src/hks_auth.c#L1-L200) [services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_permission_check.cpp1-200](https://github.com/openharmony/security_huks/blob/e99d2312/services/huks_standard/huks_service/main/os_dependency/idl/ipc/hks_permission_check.cpp#L1-L200)

 
## Testing Infrastructure

 HUKS includes comprehensive testing:

 
| Test Type | Location | Coverage |
|---|---|---|
| Module Tests | test/unittest/huks_standard_test/module_test | Individual API functions |
| Three-Stage Tests | test/unittest/huks_standard_test/three_stage_test | Init-Update-Finish patterns |
| Algorithm Tests | Various subdirectories | AES, RSA, ECC, SM2/3/4, HKDF, etc. |
| Access Control Tests | test/unittest/huks_standard_test/module_test/utils_test | Authentication token validation |
| Fuzz Tests | test/fuzz_test | API robustness testing |

 **For details, see [Testing Infrastructure](https://deepwiki.com/openharmony/security_huks/9-testing-infrastructure)**

 **Sources:** [test/unittest/huks_standard_test/module_test/BUILD.gn1-200](https://github.com/openharmony/security_huks/blob/e99d2312/test/unittest/huks_standard_test/module_test/BUILD.gn#L1-L200) [test/fuzz_test/BUILD.gn1-100](https://github.com/openharmony/security_huks/blob/e99d2312/test/fuzz_test/BUILD.gn#L1-L100)

 
## API Entry Points

 
### Primary SDK APIs

 Defined in [interfaces/inner_api/huks_standard/main/include/hks_api.h](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/include/hks_api.h):

 
| Function | Purpose | Operation Type |
|---|---|---|
| HksInitialize() | Initialize HUKS service connection | Setup |
| HksGenerateKey() | Generate a new key | One-shot |
| HksImportKey() | Import external key | One-shot |
| HksExportPublicKey() | Export public key | One-shot |
| HksDeleteKey() | Delete key | One-shot |
| HksKeyExist() | Check key existence | One-shot |
| HksEncrypt() / HksDecrypt() | Small data cipher | One-shot |
| HksSign() / HksVerify() | Digital signatures | One-shot |
| HksInit() | Start three-stage operation | Three-stage |
| HksUpdate() | Process data chunks | Three-stage |
| HksFinish() | Complete operation | Three-stage |
| HksAbort() | Cancel operation | Three-stage |

 
### Extension APIs (UKey)

 When `huks_enable_ukey_config == true`:

 
| Function | Purpose |
|---|---|
| HksRegisterProvider() | Register external crypto provider |
| HksUnregisterProvider() | Unregister provider |
| HksOpenRemoteHandle() | Open handle to external key |
| HksCloseRemoteHandle() | Close remote handle |
| HksAuthUkeyPin() | Authenticate with hardware token PIN |
| HksGetUkeyPinAuthState() | Query authentication state |
| HksExportProviderCertificates() | Export provider certificate chain |
| HksExportCertificate() | Export key certificate |
| HksGetRemoteProperty() | Query remote key properties |

 **Sources:** [interfaces/inner_api/huks_standard/main/include/hks_api.h1-300](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/include/hks_api.h#L1-L300) [interfaces/inner_api/huks_standard/main/libhukssdk.map1-100](https://github.com/openharmony/security_huks/blob/e99d2312/interfaces/inner_api/huks_standard/main/libhukssdk.map#L1-L100)

 
## Error Handling

 HUKS defines comprehensive error codes in `hks_type.h`:

 
| Error Category | Range | Examples |
|---|---|---|
| Success | 0 | HKS_SUCCESS |
| Invalid Parameters | -1000 to -1999 | HKS_ERROR_NULL_POINTER, HKS_ERROR_INVALID_ARGUMENT |
| Check Failures | -2000 to -2999 | HKS_ERROR_CHECK_GET_ALG_FAIL, HKS_ERROR_INVALID_KEY_SIZE |
| System Errors | -3000 to -3999 | HKS_ERROR_MALLOC_FAIL, HKS_ERROR_FILE_SIZE_FAIL |
| Crypto Errors | -4000 to -4999 | HKS_ERROR_CRYPTO_ENGINE_ERROR |
| Storage Errors | -5000 to -5999 | HKS_ERROR_STORAGE_FAILURE, HKS_ERROR_CORRUPT_FILE |
| Authentication Errors | -6000 to -6999 | HKS_ERROR_AUTH_VERIFY_FAILED |

 **For details, see [Error Codes](https://deepwiki.com/openharmony/security_huks/10.3-error-codes)**

 
## Navigation

 This overview provides the foundation for understanding HUKS. For detailed information:

 
 - **[Architecture](https://deepwiki.com/openharmony/security_huks/2-architecture)** - Detailed layered architecture, component interactions
 - **[Core Operations](https://deepwiki.com/openharmony/security_huks/3-core-operations)** - Key management and cryptographic operation details
 - **[Data Structures and Types](https://deepwiki.com/openharmony/security_huks/4-data-structures-and-types)** - HksBlob, HksParamSet, authentication tokens
 - **[Security Features](https://deepwiki.com/openharmony/security_huks/5-security-features)** - Access control, user authentication, storage security
 - **[UKey Extension System](https://deepwiki.com/openharmony/security_huks/6-ukey-extension-system)** - External provider integration
 - **[Storage System](https://deepwiki.com/openharmony/security_huks/7-storage-system)** - Key persistence, security levels, upgrade mechanisms
 - **[Build System and Configuration](https://deepwiki.com/openharmony/security_huks/8-build-system-and-configuration)** - Build flags, OS level adaptation
 - **[Testing Infrastructure](https://deepwiki.com/openharmony/security_huks/9-testing-infrastructure)** - Test organization and coverage
 - **[API Reference](https://deepwiki.com/openharmony/security_huks/10-api-reference)** - Complete API documentation, parameter tags, error codes
 
 **Sources:** All file references above
