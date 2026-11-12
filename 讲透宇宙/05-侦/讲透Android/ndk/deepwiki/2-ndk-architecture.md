<!-- source: DeepWiki mcp.deepwiki.com · repo android/ndk · page 2 NDK Architecture · fetched 2026-10-23 -->

# NDK Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides an in-depth examination of the Android Native Development Kit's internal architecture, covering the core system components, runtime environment, and platform integration mechanisms. The architecture encompasses the cross-compilation toolchain, build system integration, runtime environment with bionic C library, and the complete pipeline from native C/C++ code to JNI shared libraries integrated into Android applications.

For information about getting started with NDK development workflows, see [Developer Workflow](#3). For details about specific runtime components like bionic and the dynamic linker, see [Runtime Environment](#2.1). For native code compilation and integration processes, see [Native Code Integration](#2.2).

## Architectural Overview

The NDK architecture consists of several interconnected systems that enable native C/C++ development for Android applications. The architecture bridges the gap between standard POSIX development and the Android platform's unique requirements.

### Core NDK Architecture

```mermaid
graph TB
    subgraph "NDK_Core_System"
        NDKToolchain["NDK Toolchain"]
        CrossCompiler["Cross-compilation Tools"]
        AndroidAPIs["Android-specific APIs"]
    end
    
    subgraph "Build_Systems"
        NdkBuild["ndk-build"]
        CMakeIntegration["CMake Integration"]
        BuildSystemMaintainers["Build System Maintainers"]
    end
    
    subgraph "Runtime_Environment"
        BionicLibc["bionic C Library"]
        DynamicLinker["Dynamic Linker"]
        ABISupport["ABI Compatibility Layer"]
    end
    
    subgraph "Platform_Integration"
        AndroidFramework["Android Framework"]
        JNIInterface["JNI Interface"]
        SharedLibraries["Shared Libraries (.so)"]
    end
    
    subgraph "Developer_Artifacts"
        NativeCode["C/C++ Source Code"]
        CompiledLibs["Compiled Native Libraries"]
        APKIntegration["APK Integration"]
    end
    
    NDKToolchain --> CrossCompiler
    NDKToolchain --> AndroidAPIs
    CrossCompiler --> NdkBuild
    CrossCompiler --> CMakeIntegration
    
    NativeCode --> CrossCompiler
    CrossCompiler --> CompiledLibs
    CompiledLibs --> SharedLibraries
    SharedLibraries --> JNIInterface
    JNIInterface --> AndroidFramework
    
    BionicLibc --> DynamicLinker
    DynamicLinker --> ABISupport
    SharedLibraries --> BionicLibc
    
    CompiledLibs --> APKIntegration
```

Sources: [README.md:1-74]()

## Build System Architecture

The NDK supports multiple build systems through a unified architecture that abstracts the underlying cross-compilation complexity. The build system architecture provides flexibility while maintaining consistent toolchain integration.

### Build System Integration Points

```mermaid
graph LR
    subgraph "Developer_Input"
        CPPSource["C/C++ Source Files"]
        BuildConfig["Build Configuration"]
        AndroidManifest["Android.mk / CMakeLists.txt"]
    end
    
    subgraph "NDK_Build_Systems"
        NdkBuildSystem["ndk-build System"]
        CMakeBuildSystem["CMake Build System"]
        BuildSystemMaintainers["Build System Maintainers Guide"]
    end
    
    subgraph "Compilation_Pipeline"
        CrossCompilation["Cross-compilation Process"]
        ToolchainSelection["Toolchain Selection"]
        ABITargeting["ABI Targeting"]
    end
    
    subgraph "Output_Artifacts"
        SharedObjects["JNI Shared Libraries"]
        DebugSymbols["Debug Symbols"]
        APKPackaging["APK Integration"]
    end
    
    CPPSource --> NdkBuildSystem
    CPPSource --> CMakeBuildSystem
    BuildConfig --> NdkBuildSystem
    BuildConfig --> CMakeBuildSystem
    AndroidManifest --> NdkBuildSystem
    
    NdkBuildSystem --> CrossCompilation
    CMakeBuildSystem --> CrossCompilation
    BuildSystemMaintainers --> NdkBuildSystem
    BuildSystemMaintainers --> CMakeBuildSystem
    
    CrossCompilation --> ToolchainSelection
    CrossCompilation --> ABITargeting
    ToolchainSelection --> SharedObjects
    ABITargeting --> SharedObjects
    
    SharedObjects --> DebugSymbols
    SharedObjects --> APKPackaging
```

Sources: [README.md:69-71]()

The NDK build system architecture supports both `ndk-build` and CMake integration as documented in the Build System Maintainers Guide. The architecture abstracts toolchain complexity while providing developers with familiar build system interfaces.

## Runtime Integration Architecture

The NDK runtime architecture integrates with Android's unique C library implementation and dynamic linking system. This architecture ensures native code compatibility across different Android versions and device architectures.

### Runtime Environment Components

| Component | Purpose | Integration Points |
|-----------|---------|-------------------|
| bionic C Library | Android's C library implementation | System calls, POSIX compatibility |
| Dynamic Linker | Shared library loading and symbol resolution | `.so` file loading, dependency management |
| ABI Compatibility Layer | 32-bit and 64-bit architecture support | Cross-architecture compatibility |
| JNI Interface | Java-Native code bridge | Method calls, data type conversion |

```mermaid
graph TB
    subgraph "Application_Layer"
        JavaKotlinCode["Java/Kotlin Application Code"]
        JNIMethods["JNI Method Calls"]
    end
    
    subgraph "JNI_Interface_Layer"
        JNIBridge["JNI Bridge"]
        NativeMethodBinding["Native Method Binding"]
        DataTypeConversion["Data Type Conversion"]
    end
    
    subgraph "Native_Runtime_Layer"
        SharedLibraries["JNI Shared Libraries (.so)"]
        NativeFunctions["Native C/C++ Functions"]
        BionicLibc["bionic C Library"]
    end
    
    subgraph "System_Layer"
        DynamicLinker["Dynamic Linker"]
        SystemCalls["System Calls"]
        AndroidKernel["Android Linux Kernel"]
    end
    
    JavaKotlinCode --> JNIMethods
    JNIMethods --> JNIBridge
    JNIBridge --> NativeMethodBinding
    JNIBridge --> DataTypeConversion
    
    NativeMethodBinding --> SharedLibraries
    SharedLibraries --> NativeFunctions
    NativeFunctions --> BionicLibc
    
    BionicLibc --> DynamicLinker
    BionicLibc --> SystemCalls
    DynamicLinker --> AndroidKernel
    SystemCalls --> AndroidKernel
```

Sources: [README.md:40-51]()

## Cross-Compilation Toolchain Architecture

The NDK's cross-compilation architecture enables building native code on development machines for target Android devices. The toolchain handles architecture differences, API level targeting, and Android-specific optimizations.

### Toolchain Components and Flow

The cross-compilation process involves multiple stages that transform source code into Android-compatible native libraries:

```mermaid
graph LR
    subgraph "Source_Input"
        CSource["C Source Files"]
        CPPSource["C++ Source Files"]
        Headers["Header Files"]
    end
    
    subgraph "Compilation_Stages"
        Preprocessing["Preprocessing"]
        Compilation["Compilation"]
        Assembly["Assembly"]
        Linking["Linking"]
    end
    
    subgraph "Toolchain_Components"
        ClangCompiler["Clang Compiler"]
        LLVMBackend["LLVM Backend"]
        Linker["Linker (lld)"]
        Assembler["Assembler"]
    end
    
    subgraph "Android_Specifics"
        AndroidHeaders["Android API Headers"]
        BionicLibc["bionic C Library"]
        AndroidLinkerScript["Android Linker Scripts"]
    end
    
    subgraph "Output_Artifacts"
        ObjectFiles["Object Files (.o)"]
        SharedObjects["Shared Objects (.so)"]
        DebugInfo["Debug Information"]
    end
    
    CSource --> Preprocessing
    CPPSource --> Preprocessing
    Headers --> Preprocessing
    
    Preprocessing --> Compilation
    Compilation --> Assembly
    Assembly --> Linking
    
    Compilation --> ClangCompiler
    ClangCompiler --> LLVMBackend
    Assembly --> Assembler
    Linking --> Linker
    
    AndroidHeaders --> Preprocessing
    BionicLibc --> Linking
    AndroidLinkerScript --> Linking
    
    Assembly --> ObjectFiles
    Linking --> SharedObjects
    Linking --> DebugInfo
```

Sources: [README.md:1-74]()

## Platform Integration Points

The NDK architecture integrates with multiple layers of the Android platform, from the application framework down to the kernel level. These integration points ensure native code operates correctly within Android's security and runtime model.

### Android Platform Integration

| Integration Layer | NDK Components | Platform Components |
|-------------------|----------------|-------------------|
| Application Framework | JNI shared libraries | Android Runtime (ART) |
| Native Framework | Android-specific APIs | Native system services |
| C Library Layer | bionic integration | System call interface |
| Kernel Interface | System calls | Linux kernel |

The integration architecture ensures that native code compiled with the NDK can interact seamlessly with Android's Java-based application framework while maintaining access to lower-level system capabilities through the bionic C library and system call interface.

## ABI and Compatibility Architecture

The NDK supports multiple Application Binary Interfaces (ABIs) to ensure compatibility across different Android device architectures. The ABI compatibility layer handles architecture-specific differences and ensures consistent behavior across 32-bit and 64-bit platforms.

### ABI Support Matrix

```mermaid
graph TB
    subgraph "NDK_ABI_Support"
        ARM64["arm64-v8a (64-bit)"]
        ARM32["armeabi-v7a (32-bit)"]
        X86_64["x86_64 (64-bit)"]
        X86_32["x86 (32-bit)"]
    end
    
    subgraph "Compatibility_Layer"
        ABICompat["ABI Compatibility Layer"]
        BitCompatibility["32-bit/64-bit Support"]
        ArchSpecific["Architecture-specific Optimizations"]
    end
    
    subgraph "Runtime_Considerations"
        DynamicLinking["Dynamic Linking"]
        SymbolResolution["Symbol Resolution"]
        MemoryLayout["Memory Layout"]
    end
    
    ARM64 --> ABICompat
    ARM32 --> ABICompat
    X86_64 --> ABICompat
    X86_32 --> ABICompat
    
    ABICompat --> BitCompatibility
    ABICompat --> ArchSpecific
    
    BitCompatibility --> DynamicLinking
    ArchSpecific --> SymbolResolution
    DynamicLinking --> MemoryLayout
```

Sources: [README.md:50-51]()

The ABI architecture addresses 32-bit specific issues and ensures proper dynamic linking behavior across different Android releases, as documented in the bionic dynamic linker changes and 32-bit ABI documentation.

---

