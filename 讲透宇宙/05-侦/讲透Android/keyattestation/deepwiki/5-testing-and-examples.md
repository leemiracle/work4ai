<!-- source: DeepWiki mcp.deepwiki.com · repo android/keyattestation · page 5 Testing and Examples · fetched 2026-10-23 -->

# Testing and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [build.gradle.kts](build.gradle.kts)
- [src/main/kotlin/testing/TestUtils.kt](src/main/kotlin/testing/TestUtils.kt)
- [testdata/akita/sdk34/SB_RSA_NONE.json](testdata/akita/sdk34/SB_RSA_NONE.json)

</details>



This document provides an overview of the testing framework and example attestation data included with the Android Key Attestation verification library. The testing infrastructure is designed to validate the library against real-world attestation data from various Android devices and security configurations.

For detailed information about specific testing utilities, see [Test Framework](#5.1). For comprehensive attestation examples, see [Attestation Examples](#5.2), [StrongBox vs TEE Examples](#5.3), and [Device Identity Attestations](#5.4).

## Testing Architecture Overview

The testing framework consists of three main components: test utilities for loading attestation data, a comprehensive set of real-world attestation examples, and support for both production and test trust anchor configurations.

### Testing Infrastructure

```mermaid
graph TD
    subgraph "Test Utilities"
        TestUtils["TestUtils"]
        CertPathReader["readCertPath()"]
        JSONAdapters["JSON Adapters"]
        ProdAnchors["prodAnchors"]
    end
    
    subgraph "Test Data Organization"
        TestDataPath["testdata/"]
        DeviceExamples["akita/sdk34/"]
        AttestationFiles["*.pem, *.json"]
    end
    
    subgraph "Generated Trust Anchors"
        RootsJSON["roots.json"]
        GradleTask["googleTrustAnchors task"]
        GeneratedAnchors["GoogleTrustAnchors.kt"]
    end
    
    subgraph "Test Configuration Types"
        StrongBoxRSA["SB_RSA_NONE.json"]
        TEERSA["TEE_RSA_examples"]
        ECExamples["EC key examples"]
        DeviceIdentity["Device identity data"]
    end
    
    TestUtils --> CertPathReader
    TestUtils --> JSONAdapters
    TestUtils --> ProdAnchors
    TestUtils --> TestDataPath
    
    TestDataPath --> DeviceExamples
    DeviceExamples --> AttestationFiles
    
    RootsJSON --> GradleTask
    GradleTask --> GeneratedAnchors
    
    AttestationFiles --> StrongBoxRSA
    AttestationFiles --> TEERSA
    AttestationFiles --> ECExamples
    AttestationFiles --> DeviceIdentity
```

**Sources:** [src/main/kotlin/testing/TestUtils.kt:45-76](), [build.gradle.kts:52-86]()

## Test Data Organization

The test data is systematically organized to cover different Android device configurations and security levels. The data includes both certificate chains (PEM format) and parsed attestation information (JSON format).

### Test Data Structure

```mermaid
graph LR
    subgraph "File System Layout"
        TestDataRoot["testdata/"]
        DeviceFolder["akita/sdk34/"]
        StrongBoxFiles["SB_*.json"]
        TEEFiles["TEE_*.json"]
        CertFiles["*.pem"]
    end
    
    subgraph "Attestation Types"
        RSAAttestation["RSA Keys"]
        ECAttestation["EC Keys"]
        AuthRequirements["Auth Requirements"]
        SecurityLevels["TEE vs StrongBox"]
    end
    
    subgraph "Data Formats"
        PEMCerts["PEM Certificate Chains"]
        JSONData["JSON Attestation Data"]
        KeyDescriptions["KeyDescription Objects"]
    end
    
    TestDataRoot --> DeviceFolder
    DeviceFolder --> StrongBoxFiles
    DeviceFolder --> TEEFiles
    DeviceFolder --> CertFiles
    
    StrongBoxFiles --> RSAAttestation
    TEEFiles --> ECAttestation
    CertFiles --> AuthRequirements
    
    PEMCerts --> KeyDescriptions
    JSONData --> KeyDescriptions
```

**Sources:** [src/main/kotlin/testing/TestUtils.kt:47-50](), [testdata/akita/sdk34/SB_RSA_NONE.json:1-38]()

## Core Testing Utilities

The `TestUtils` object provides essential functionality for loading and parsing test attestation data. It handles both certificate chain parsing from PEM files and JSON serialization of attestation data structures.

| Function | Purpose | Input Format | Output Type |
|----------|---------|--------------|-------------|
| `readCertPath(subpath)` | Load certificate chain from testdata | PEM file path | `KeyAttestationCertPath` |
| `readCertPath(reader)` | Parse certificate chain from reader | PEM format | `KeyAttestationCertPath` |
| `prodAnchors` | Load production trust anchors | roots.json | `Set<TrustAnchor>` |
| `toJson()` | Serialize KeyDescription | `KeyDescription` | JSON string |
| `toKeyDescription()` | Deserialize KeyDescription | JSON string | `KeyDescription` |

**Sources:** [src/main/kotlin/testing/TestUtils.kt:49-76](), [src/main/kotlin/testing/TestUtils.kt:110-112]()

## JSON Serialization Support

The testing framework includes custom JSON adapters to handle complex data types used in attestation data. These adapters ensure proper serialization and deserialization of binary data and specialized types.

### Custom JSON Adapters

```mermaid
graph TD
    subgraph "JSON Serialization"
        GsonBuilder["GsonBuilder"]
        Base64Adapter["Base64ByteStringAdapter"]
        BigIntAdapter["BigIntegerAdapter"] 
        PatchLevelAdapter["PatchLevelAdapter"]
        FinalGson["gson instance"]
    end
    
    subgraph "Data Type Handling"
        ByteStringType["ByteString ↔ Base64"]
        BigIntegerType["BigInteger ↔ String"]
        PatchLevelType["PatchLevel ↔ String"]
    end
    
    subgraph "Conversion Functions"
        ToJSON["KeyDescription.toJson()"]
        FromJSON["String.toKeyDescription()"]
    end
    
    GsonBuilder --> Base64Adapter
    GsonBuilder --> BigIntAdapter
    GsonBuilder --> PatchLevelAdapter
    GsonBuilder --> FinalGson
    
    Base64Adapter --> ByteStringType
    BigIntAdapter --> BigIntegerType
    PatchLevelAdapter --> PatchLevelType
    
    FinalGson --> ToJSON
    FinalGson --> FromJSON
```

**Sources:** [src/main/kotlin/testing/TestUtils.kt:78-112]()

## Example Attestation Data Structure

The test data includes comprehensive examples showing the structure of real Android Key Attestation data. Each example demonstrates different security configurations and device characteristics.

### StrongBox RSA Attestation Example

The following table shows the key fields from a StrongBox RSA attestation example:

| Field | Value | Description |
|-------|--------|-------------|
| `attestationVersion` | "300" | KeyMint version 3.0 |
| `attestationSecurityLevel` | "STRONG_BOX" | Hardware security module |
| `keyMintVersion` | "300" | KeyMint implementation version |
| `attestationChallenge` | "Y2hhbGxlbmdl" | Base64 encoded challenge |
| `hardwareEnforced.purposes` | ["2"] | Encryption purpose |
| `hardwareEnforced.keySize` | "2048" | RSA key size |
| `hardwareEnforced.algorithms` | "1" | RSA algorithm |
| `hardwareEnforced.origin` | "GENERATED" | Key generated in hardware |
| `softwareEnforced.creationDateTime` | "1727389887639" | Unix timestamp |

**Sources:** [testdata/akita/sdk34/SB_RSA_NONE.json:1-38]()

## Trust Anchor Management

The testing framework supports both production and test trust anchor configurations through a dual approach: build-time generated anchors for production use and runtime loading for testing flexibility.

### Trust Anchor Generation Flow

```mermaid
sequenceDiagram
    participant BuildSystem as "Gradle Build"
    participant RootsJSON as "roots.json"
    participant GenerateTask as "googleTrustAnchors"
    participant GeneratedCode as "GoogleTrustAnchors.kt"
    participant TestUtils as "TestUtils"
    participant Runtime as "Test Runtime"
    
    BuildSystem->>RootsJSON: "Read trust anchor data"
    BuildSystem->>GenerateTask: "Execute task"
    GenerateTask->>GeneratedCode: "Generate Kotlin code"
    
    Runtime->>TestUtils: "prodAnchors access"
    TestUtils->>RootsJSON: "Read directly"
    TestUtils->>Runtime: "Return TrustAnchor set"
    
    Runtime->>GeneratedCode: "Production usage"
    GeneratedCode->>Runtime: "Return TrustAnchor set"
```

**Sources:** [build.gradle.kts:52-86](), [src/main/kotlin/testing/TestUtils.kt:67-72]()

## Testing Dependencies and Configuration

The project uses several testing libraries to ensure comprehensive validation of the attestation verification process:

- **JUnit Platform**: Modern testing framework with JUnit 4 compatibility
- **Test Parameter Injector**: Google's parameterized testing library
- **Truth**: Fluent assertion library for clear test failures
- **Gson**: JSON serialization for test data handling
- **BouncyCastle**: Cryptographic operations and certificate parsing

**Sources:** [build.gradle.kts:33-47]()

---

