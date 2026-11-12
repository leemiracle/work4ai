<!-- source: DeepWiki mcp.deepwiki.com · repo android/security-certification-resources · page 4 Build System and Code Generation · fetched 2026-10-23 -->

# Build System and Code Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [niap-cc/Permissions/Companion/.aiexclude](niap-cc/Permissions/Companion/.aiexclude)
- [niap-cc/Permissions/Companion/gradle/wrapper/gradle-wrapper.properties](niap-cc/Permissions/Companion/gradle/wrapper/gradle-wrapper.properties)
- [niap-cc/Permissions/Tester/.aiexclude](niap-cc/Permissions/Tester/.aiexclude)
- [niap-cc/Permissions/Tester/.gitignore](niap-cc/Permissions/Tester/.gitignore)
- [niap-cc/Permissions/Tester/app/src/main/res/xml/preference.xml](niap-cc/Permissions/Tester/app/src/main/res/xml/preference.xml)
- [niap-cc/Permissions/Tester/build.gradle.kts](niap-cc/Permissions/Tester/build.gradle.kts)
- [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt](niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt)
- [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/test/kotlin/org/example/CodePorterPluginTest.kt](niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/test/kotlin/org/example/CodePorterPluginTest.kt)
- [niap-cc/Permissions/TransactIds/.aiexclude](niap-cc/Permissions/TransactIds/.aiexclude)
- [niap-cc/Permissions/TransactIds/app/build.gradle](niap-cc/Permissions/TransactIds/app/build.gradle)
- [niap-cc/Permissions/TransactIds/build.gradle.kts](niap-cc/Permissions/TransactIds/build.gradle.kts)
- [niap-cc/Permissions/TransactIds/gradle/wrapper/gradle-wrapper.properties](niap-cc/Permissions/TransactIds/gradle/wrapper/gradle-wrapper.properties)

</details>



This document covers the multi-module Gradle build system and automated code generation infrastructure that supports the Android Security Certification Resources framework. The build system orchestrates compilation of multiple Android applications with different signing configurations, while code generation tools automatically create test modules and supporting classes.

For detailed information about the generated permission test modules, see [Permission Test Modules](#5.2). For information about the runtime applications produced by this build system, see [Supporting Applications](#3).

## Multi-Module Build Architecture

The project uses a multi-module Gradle build system with several distinct Android applications, each serving different roles in the testing ecosystem. The build configuration supports both platform-signed and standard-signed variants to test different permission scenarios.

### Build System Overview

```mermaid
graph TB
    subgraph "Root Build Configuration"
        ROOT_TESTER["Tester/build.gradle.kts<br/>Root Build Script"]
        ROOT_TRANSACT["TransactIds/build.gradle.kts<br/>Root Build Script"]
    end
    
    subgraph "Application Modules"
        TESTER_APP["Tester/app/build.gradle<br/>Main Testing App"]
        TRANSACT_APP["TransactIds/app/build.gradle<br/>Binder Discovery App"]
        COMPANION_APP["Companion/app/build.gradle<br/>Support Services App"]
    end
    
    subgraph "Code Generation"
        CODE_PORTER["CodePorterPlugin<br/>AST-based Test Generation"]
        BIND_SERVICE["BindServiceCodeGenPlugin<br/>Service Generation"]
    end
    
    subgraph "Build Artifacts"
        PLATFORM_SIGNED["Platform-signed APKs<br/>System-level Permissions"]
        NORMAL_SIGNED["Normal-signed APKs<br/>Standard Permissions"]
        GENERATED_TESTS["Generated Test Modules<br/>*PermissionTestModule.java"]
    end
    
    ROOT_TESTER --> TESTER_APP
    ROOT_TRANSACT --> TRANSACT_APP
    
    CODE_PORTER --> GENERATED_TESTS
    TESTER_APP --> CODE_PORTER
    
    TESTER_APP --> PLATFORM_SIGNED
    TESTER_APP --> NORMAL_SIGNED
    TRANSACT_APP --> PLATFORM_SIGNED
    COMPANION_APP --> PLATFORM_SIGNED
```

**Sources:** [niap-cc/Permissions/Tester/build.gradle.kts:18-32](), [niap-cc/Permissions/TransactIds/build.gradle.kts:18-29](), [niap-cc/Permissions/TransactIds/app/build.gradle:17-58]()

### Platform Signing Configuration

The build system implements platform signing to enable testing of signature-protected permissions that require system-level access. This configuration is critical for comprehensive permission testing.

| Module | Platform Signing | Purpose |
|--------|------------------|---------|
| Tester | Required | Tests signature permissions requiring platform certificate |
| TransactIds | Required | Accesses system services for binder transaction discovery |
| Companion | Required | Sets up test environment with privileged operations |

The signing configuration uses a shared platform keystore:

```mermaid
graph LR
    KEYSTORE["platform.jks<br/>Platform Keystore"] --> TESTER["Tester App<br/>Platform Signed"]
    KEYSTORE --> TRANSACT["TransactIds App<br/>Platform Signed"]  
    KEYSTORE --> COMPANION["Companion App<br/>Platform Signed"]
    
    TESTER --> SYS_SERVICES["Android System Services<br/>Privileged Access"]
    TRANSACT --> BINDER_DISCOVERY["Binder Transaction Discovery<br/>Hidden API Access"]
    COMPANION --> TEST_SETUP["Test Environment Setup<br/>Media Files, Services"]
```

**Sources:** [niap-cc/Permissions/TransactIds/app/build.gradle:24-42]()

## Code Generation Pipeline

The build system includes sophisticated code generation tools that automatically create test modules and supporting classes from existing permission tester implementations.

### CodePorterPlugin Architecture

The `CodePorterPlugin` uses ANTLR-based Java AST parsing to analyze existing `*PermissionTester.java` files and generate corresponding `*PermissionTestModule.java` classes with JUnit-style test methods.

```mermaid
graph TD
    subgraph "Input Sources"
        TESTER_JAVA["*PermissionTester.java<br/>Test Implementation Classes"]
        PERM_DEFS["Permission Definitions<br/>SignaturePermissions, InternalPermissions"]
    end
    
    subgraph "CodePorterPlugin Processing"
        JAVA_LEXER["JavaLexer<br/>Tokenization"]
        JAVA_PARSER["JavaParser<br/>AST Generation"]
        AST_LISTENER["AstListener<br/>Permission Test Extraction"]
    end
    
    subgraph "Code Generation Logic"
        TEST_CASE_SOURCE["TestCaseSource<br/>Data Structure"]
        CASE_FORMAT["CaseFormat Conversion<br/>UPPER_UNDERSCORE to UPPER_CAMEL"]
        TEMPLATE_GEN["Template Generation<br/>JUnit Test Methods"]
    end
    
    subgraph "Generated Output"
        TEST_MODULES["*PermissionTestModule.java<br/>Generated Test Classes"]
        GEN_OUT_JAVA["package/gen/java/<br/>Output Directory"]
    end
    
    TESTER_JAVA --> JAVA_LEXER
    JAVA_LEXER --> JAVA_PARSER
    JAVA_PARSER --> AST_LISTENER
    
    AST_LISTENER --> TEST_CASE_SOURCE
    TEST_CASE_SOURCE --> CASE_FORMAT
    CASE_FORMAT --> TEMPLATE_GEN
    
    TEMPLATE_GEN --> TEST_MODULES
    TEST_MODULES --> GEN_OUT_JAVA
```

**Sources:** [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:47-64](), [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:199-223]()

### Permission Test Extraction Process

The code generation process extracts permission test definitions from `PermissionTest` object instantiations within the source testers and converts them into individual test methods:

```mermaid
sequenceDiagram
    participant CP as "CodePorterPlugin"
    participant AL as "AstListener"
    participant IAL as "InnerArgListener"
    participant TCS as "TestCaseSource"
    participant TG as "Template Generator"
    
    CP->>AL: "Walk AST for *.java files"
    AL->>AL: "Find .put() method calls"
    AL->>IAL: "Process PermissionTest constructors"
    IAL->>TCS: "Extract permission, sdkMin, sdkMax, impl"
    TCS->>TCS: "Convert UPPER_UNDERSCORE to UPPER_CAMEL"
    TCS->>TG: "Generate test method template"
    TG->>CP: "Write *PermissionTestModule.java"
```

**Sources:** [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:96-168](), [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:272-311]()

### Generated Test Module Structure

The `CodePorterPlugin` generates test modules following a consistent pattern with SDK version constraints and permission annotations:

| Generated Element | Purpose | Example |
|------------------|---------|---------|
| `@PermissionTestModule` | Class-level annotation | `name="Signature Test Cases"` |
| `@PermissionTest` | Method-level annotation | `permission=CAMERA, sdkMin=28` |
| Test Method Names | Camel case conversion | `testManageUsersPermission()` |
| SDK Constraints | Version-specific testing | `sdkMin=31, sdkMax=34` |

**Sources:** [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:260-268](), [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:301-306]()

## Build Dependencies and Tools

The build system integrates multiple specialized tools and dependencies to support both standard Android development and advanced system-level testing capabilities.

### Core Build Dependencies

```mermaid
graph TB
    subgraph "Android Build Tools"
        AGP["Android Gradle Plugin<br/>8.4.2 / 8.8.2"]
        SDK35["Android SDK 35<br/>Target/Compile SDK"]
        MIN_SDK["Min SDK 28<br/>Android 9+"]
    end
    
    subgraph "Code Generation Tools"
        ANTLR["ANTLR Runtime<br/>Java AST Parsing"]
        JAVAPARSER["JavaParser<br/>3.3.0"]
        GUAVA["Google Guava<br/>24.1-jre"]
    end
    
    subgraph "JSON Processing"
        JACKSON_CORE["Jackson Core<br/>2.17.2"]
        JACKSON_DATABIND["Jackson Databind<br/>2.17.2"]
    end
    
    subgraph "Testing Framework"
        ANDROIDX_TEST["AndroidX Test<br/>JUnit, Espresso"]
        JUNIT["JUnit 4.13.2<br/>Unit Testing"]
    end
    
    AGP --> SDK35
    SDK35 --> MIN_SDK
    
    ANTLR --> JAVAPARSER
    JAVAPARSER --> GUAVA
    
    JACKSON_CORE --> JACKSON_DATABIND
```

**Sources:** [niap-cc/Permissions/Tester/build.gradle.kts:24-27](), [niap-cc/Permissions/TransactIds/app/build.gradle:67-83]()

### Gradle Wrapper Configuration

The project uses different Gradle wrapper versions across modules to ensure compatibility with various Android Gradle Plugin versions:

| Module | Gradle Version | Purpose |
|--------|----------------|---------|
| TransactIds | 8.10.2 | Latest features for binder discovery |
| Companion | 8.7 | Stable version for support services |
| Tester | 8.4.2 | Compatible with complex code generation |

**Sources:** [niap-cc/Permissions/TransactIds/gradle/wrapper/gradle-wrapper.properties:4](), [niap-cc/Permissions/Companion/gradle/wrapper/gradle-wrapper.properties:3]()

## Build Artifacts and Output Structure

The build system produces multiple APK variants and generated source files organized in a structured output directory:

```mermaid
graph TB
    subgraph "Build Outputs"
        PACKAGE_DIR["package/<br/>Build Artifacts"]
        GEN_JAVA["package/gen/java/<br/>Generated Source"]
        APKS["APK Variants<br/>Platform & Normal Signed"]
    end
    
    subgraph "Generated Sources"
        TEST_MODULES["*PermissionTestModule.java<br/>Generated Test Classes"]
        CONSTANTS["Permission Constants<br/>SignaturePermissions.java"]
        SERVICES["Generated Services<br/>TestBind*Services"]
    end
    
    subgraph "APK Variants"
        PLATFORM_APK["Platform-signed APKs<br/>System Permissions"]
        DEBUG_APK["Debug APKs<br/>Development Testing"]
        RELEASE_APK["Release APKs<br/>Production Testing"]
    end
    
    PACKAGE_DIR --> GEN_JAVA
    PACKAGE_DIR --> APKS
    
    GEN_JAVA --> TEST_MODULES
    GEN_JAVA --> CONSTANTS
    GEN_JAVA --> SERVICES
    
    APKS --> PLATFORM_APK
    APKS --> DEBUG_APK
    APKS --> RELEASE_APK
```

**Sources:** [niap-cc/Permissions/Tester/gradle/code-porter-plugin/plugin/src/main/kotlin/niap/codeporter/CodePorterPlugin.kt:73-75](), [niap-cc/Permissions/Tester/.gitignore:44-45]()

---

