<!-- source: DeepWiki mcp.deepwiki.com · repo android/security-certification-resources · page 1 Overview · fetched 2026-10-23 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [niap-cc/Permissions/Companion/app/build.gradle](niap-cc/Permissions/Companion/app/build.gradle)
- [niap-cc/Permissions/Companion/app/src/main/AndroidManifest.xml](niap-cc/Permissions/Companion/app/src/main/AndroidManifest.xml)
- [niap-cc/Permissions/Companion/app/src/main/java/com/android/certifications/niap/permissions/companion/MainActivity.java](niap-cc/Permissions/Companion/app/src/main/java/com/android/certifications/niap/permissions/companion/MainActivity.java)
- [niap-cc/Permissions/Companion/app/src/main/res/layout/activity_main.xml](niap-cc/Permissions/Companion/app/src/main/res/layout/activity_main.xml)
- [niap-cc/Permissions/Companion/build.gradle.kts](niap-cc/Permissions/Companion/build.gradle.kts)
- [niap-cc/Permissions/Tester/app/build.gradle](niap-cc/Permissions/Tester/app/build.gradle)
- [niap-cc/Permissions/Tester/app/src/androidTest/AndroidManifest.xml](niap-cc/Permissions/Tester/app/src/androidTest/AndroidManifest.xml)
- [niap-cc/Permissions/Tester/app/src/main/AndroidManifest.xml](niap-cc/Permissions/Tester/app/src/main/AndroidManifest.xml)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/InstallPermissionTester.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/InstallPermissionTester.java)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/SignaturePermissionTester.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/SignaturePermissionTester.java)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/activities/MainActivity.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/activities/MainActivity.java)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/config/SignatureDependentPermissionConfiguration.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/config/SignatureDependentPermissionConfiguration.java)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/SdkV_Transacts.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/SdkV_Transacts.java)
- [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/Transacts.java](niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/Transacts.java)
- [niap-cc/Permissions/Tester/app/src/noperm/AndroidManifest.xml](niap-cc/Permissions/Tester/app/src/noperm/AndroidManifest.xml)
- [niap-cc/Permissions/Tester/app/src/normal/AndroidManifest.xml](niap-cc/Permissions/Tester/app/src/normal/AndroidManifest.xml)
- [niap-cc/Permissions/Tester/app/src/platform/AndroidManifest.xml](niap-cc/Permissions/Tester/app/src/platform/AndroidManifest.xml)
- [niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/MainActivity.java](niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/MainActivity.java)
- [niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/Transacts.java](niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/Transacts.java)

</details>



This document provides an overview of the Android Security Certification Resources repository, a comprehensive testing framework designed for NIAP (National Information Assurance Partnership) Common Criteria certification of Android devices. The framework validates that Android platform permissions are properly enforced by testing various permission protection levels through direct API invocation and system service interaction.

The repository contains multiple specialized applications that work together to thoroughly test Android's permission system, from basic install permissions to complex signature-level permissions that require platform signing. For detailed information about specific permission testing approaches, see [Permission Testing Framework](#2). For details about the build system and code generation tools, see [Build System and Code Generation](#4).

## System Architecture

The Android Security Certification Resources framework consists of four main applications that work together to provide comprehensive permission testing capabilities:

```mermaid
graph TB
    subgraph "Core Testing Applications"
        TESTER["PermissionTester<br/>(MainActivity)"]
        COMPANION["Companion App<br/>(MainActivity)"]
        TRANSACT_IDS["TransactIds App<br/>(MainActivity)"]
        HUBBLE["Hubble App<br/>(Uraniborg)"]
    end
    
    subgraph "Permission Testing Framework"
        BPT["BasePermissionTester"]
        SPT["SignaturePermissionTester"]
        IPT["InstallPermissionTester"]
        RPT["RuntimePermissionTester"]
        INPT["InternalPermissionTester"]
    end
    
    subgraph "System Integration Layer"
        TRANSACTS["Transacts Utility"]
        REFLECTION["ReflectionUtils"]
        CONFIG["TestConfiguration"]
    end
    
    subgraph "Android System"
        SERVICES["System Services<br/>(ActivityManager, PackageManager, etc.)"]
        BINDER["Binder IPC Layer"]
    end
    
    TESTER --> BPT
    BPT --> SPT
    BPT --> IPT
    BPT --> RPT
    BPT --> INPT
    
    SPT --> TRANSACTS
    INPT --> TRANSACTS
    SPT --> REFLECTION
    
    TRANSACTS --> BINDER
    REFLECTION --> SERVICES
    BINDER --> SERVICES
    
    COMPANION --> SERVICES
    TRANSACT_IDS --> BINDER
    HUBBLE --> SERVICES
    
    CONFIG --> BPT
```

**Sources:** [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/activities/MainActivity.java:120-400](), [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/SignaturePermissionTester.java:280-320](), [niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/MainActivity.java:83-142]()

## Core Applications

### Permission Tester Application
The main testing application (`MainActivity`) orchestrates permission tests across different protection levels. It uses a configuration-driven approach where `ConfigurationFactory` provides different test scenarios, and specialized tester classes handle specific permission types.

```mermaid
graph LR
    USER["User"] --> MAIN_ACT["MainActivity"]
    MAIN_ACT --> CONFIG_FACTORY["ConfigurationFactory"]
    CONFIG_FACTORY --> TEST_CONFIGS["TestConfiguration<br/>Implementations"]
    
    TEST_CONFIGS --> DEFAULT_CONFIG["DefaultConfiguration"]
    TEST_CONFIGS --> SIG_DEPENDENT["SignatureDependentPermissionConfiguration"]
    TEST_CONFIGS --> RUNTIME_DEP["RuntimeDependentConfiguration"]
    
    MAIN_ACT --> SIGNATURE_TESTER["SignaturePermissionTester"]
    MAIN_ACT --> INSTALL_TESTER["InstallPermissionTester"]
    MAIN_ACT --> RUNTIME_TESTER["RuntimePermissionTester"]
    MAIN_ACT --> INTERNAL_TESTER["InternalPermissionTester"]
    
    SIGNATURE_TESTER --> TRANSACTS_UTIL["Transacts"]
    INTERNAL_TESTER --> REFLECTION_UTILS["ReflectionUtils"]
```

**Sources:** [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/activities/MainActivity.java:255-280](), [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/config/SignatureDependentPermissionConfiguration.java:44-117]()

### TransactIds Discovery Application
The `TransactIds` application (`MainActivity`) dynamically discovers binder transaction IDs for system services. Since transaction IDs can vary between device implementations, this tool uses reflection to query AIDL stub classes and generate device-specific transaction mappings.

### Companion Application
The `Companion` application prepares the test environment by setting up required resources like media files, configuring location services, and providing test services that other applications can bind to for permission validation.

### Hubble Data Collection
The `Hubble` application (part of the Uraniborg project) collects device information and preinstalled application data for analysis during certification testing.

**Sources:** [niap-cc/Permissions/TransactIds/app/src/main/java/com/android/certifications/niap/permissions/transactids/MainActivity.java:73-142](), [niap-cc/Permissions/Companion/app/src/main/java/com/android/certifications/niap/permissions/companion/MainActivity.java:86-150]()

## Permission Testing Framework

The framework implements a hierarchical testing architecture with `BasePermissionTester` as the foundation and specialized testers for different permission protection levels:

```mermaid
graph TB
    BPT["BasePermissionTester<br/>(Abstract Base)"]
    
    BPT --> SPT["SignaturePermissionTester<br/>(Platform Signature Required)"]
    BPT --> IPT["InstallPermissionTester<br/>(Install-time Grants)"]
    BPT --> RPT["RuntimePermissionTester<br/>(User Consent Required)"]
    BPT --> INPT["InternalPermissionTester<br/>(Hidden APIs)"]
    BPT --> PPT["PrivilegedPermissionTester<br/>(Priv-app Required)"]
    BPT --> DPPT["DevicePolicyPermissionTester<br/>(Device Admin)"]
    
    SPT --> BINDER_IPC["Direct Binder IPC<br/>(Transacts.invokeTransact)"]
    INPT --> HIDDEN_API["Hidden API Access<br/>(ReflectionUtils.invokeReflectionCall)"]
    IPT --> PUBLIC_API["Public Android APIs"]
    RPT --> PERMISSION_REQ["Permission Request Dialog"]
    
    BINDER_IPC --> SYS_SERVICES["System Services<br/>(ActivityManager, PackageManager,<br/>DisplayManager, etc.)"]
    HIDDEN_API --> SYS_SERVICES
    PUBLIC_API --> SYS_SERVICES
```

**Sources:** [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/SignaturePermissionTester.java:280-380](), [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/InstallPermissionTester.java:213-260]()

## Build System and Multi-Module Structure

The project uses a sophisticated Gradle build system with automated code generation and multiple application variants:

| Component | Purpose | Build Variants |
|-----------|---------|----------------|
| Permission Tester | Main testing app | `normal`, `platform`, `noperm` |
| Companion | Test environment setup | `debug`, `release` |
| TransactIds | Transaction ID discovery | Platform-signed only |
| Hubble | Device data collection | Standard build |

The build system includes custom Gradle plugins for code generation:
- `CodePorterPlugin` - Generates test modules from existing tester classes
- `BindServiceCodeGenPlugin` - Creates service classes for BIND_* permission testing
- Permission constant generation from `permissions.json`

**Sources:** [niap-cc/Permissions/Tester/app/build.gradle:19-137](), [niap-cc/Permissions/Companion/app/build.gradle:17-96](), [niap-cc/Permissions/Companion/build.gradle.kts:43-148]()

## System Service Integration

The framework achieves comprehensive permission testing through multiple integration approaches:

```mermaid
graph LR
    subgraph "Testing Approaches"
        PUBLIC_API["Public Android APIs"]
        BINDER_DIRECT["Direct Binder Calls"]
        REFLECTION["Reflection Access"]
    end
    
    subgraph "Integration Layer"
        TRANSACTS["Transacts Utility"]
        REFLECTION_UTILS["ReflectionUtils"]
        STD_ANDROID["Standard Android SDK"]
    end
    
    subgraph "Target Services"
        ACTIVITY_MGR["ActivityManager"]
        PACKAGE_MGR["PackageManager"]
        DISPLAY_MGR["DisplayManager"]
        POWER_MGR["PowerManager"]
        OTHER_SERVICES["50+ System Services"]
    end
    
    PUBLIC_API --> STD_ANDROID
    BINDER_DIRECT --> TRANSACTS
    REFLECTION --> REFLECTION_UTILS
    
    STD_ANDROID --> ACTIVITY_MGR
    TRANSACTS --> PACKAGE_MGR
    REFLECTION_UTILS --> DISPLAY_MGR
    
    TRANSACTS --> POWER_MGR
    REFLECTION_UTILS --> OTHER_SERVICES
```

The `Transacts` utility class defines constants for over 50 system services and provides device-specific transaction ID mappings through generated subclasses like `SdkV_Transacts` for different Android API levels.

**Sources:** [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/Transacts.java:59-320](), [niap-cc/Permissions/Tester/app/src/main/java/com/android/certifications/niap/permissions/utils/SdkV_Transacts.java:21-500]()

---

