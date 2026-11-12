<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/OpenSMA · page 2 Build and Test Infrastructure · fetched 2026-10-26 -->

# Build and Test Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [README.md](README.md)

</details>



This document covers the Universal Build System (UBS) and comprehensive testing framework that enables multi-language development across C, C++, and Ada in the OpenSMA project. UBS provides a makefile-based build orchestration system with platform abstraction, plugin architecture, and integrated testing capabilities.

For information about the specific testing implementations within individual modules, see [Self-Tests and Validation](#2.3). For details about the UBS build system mechanics, see [UBS Build System](#2.1). For the testing framework and assertion mechanisms, see [Testing Framework](#2.2).

## UBS Architecture Overview

The Universal Build System is structured as a modular makefile-based system that orchestrates compilation, linking, testing, and static analysis across multiple programming languages and target platforms.

### Core UBS Components

```mermaid
graph TB
    subgraph "UBS Entry Points"
        UBSMAIN["ubs-main.mk<br/>Main orchestration"]
        UBSMK["ubs.mk<br/>User interface"]
    end
    
    subgraph "Configuration Layer"
        UBSCONFIG["ubs-config.mk<br/>Base configuration"]
        UBSPROJECT["ubs-project.mk<br/>Project settings"] 
        UBSPLATFORM["ubs-platform.mk<br/>Platform support"]
        UBSPOSTCONFIG["ubs-post-config.mk<br/>Final processing"]
    end
    
    subgraph "Build Engine"
        UBSRULES["ubs-rules.mk<br/>Compilation rules"]
        UBSUTILS["ubs-utils.mk<br/>Helper functions"]
        UBSPRINTER["ubs-printer.mk<br/>Console output"]
    end
    
    subgraph "Extension Systems"
        UBSPLUGIN["ubs-plugin.mk<br/>Plugin loader"]
        UBSREQ["ubs-requirements.mk<br/>Tool validation"]
        UBSCLEAN["ubs-clean.mk<br/>Cleanup rules"]
    end
    
    subgraph "Testing & Analysis"
        UBSUNITTEST["ubs-unittest.mk<br/>Test execution"]
        UBSCOVERAGE["ubs-coverage.mk<br/>Coverage analysis"]
        UBSSTATICANALYSIS["ubs-static-analysis.mk<br/>Code analysis"]
    end
    
    UBSMAIN --> UBSCONFIG
    UBSMAIN --> UBSUTILS
    UBSMAIN --> UBSPRINTER
    UBSMAIN --> UBSPLUGIN
    UBSMAIN --> UBSREQ
    UBSMAIN --> UBSCLEAN
    UBSMAIN --> UBSPLATFORM
    UBSMAIN --> UBSPROJECT
    UBSMAIN --> UBSUNITTEST
    UBSMAIN --> UBSCOVERAGE
    UBSMAIN --> UBSSTATICANALYSIS
    UBSMAIN --> UBSPOSTCONFIG
    UBSMAIN --> UBSRULES
    
    UBSMK --> UBSMAIN
```

**Sources:** [corepdk/ubs/src/ubs/ubs-main.mk:18-35](), [corepdk/ubs/src/ubs/ubs.mk:19]()

### Build Process Flow

```mermaid
graph TD
    subgraph "Initialization"
        A["make build"]
        B["Load user.mk"]
        C["Load ubs-config.mk"] 
        D["Platform validation"]
        E["Project validation"]
    end
    
    subgraph "Configuration Processing"
        F["Process SOURCES"]
        G["Generate UBS_OBJECTS"]
        H["Process INCLUDES"]
        I["Setup compiler flags"]
        J["Generate global defines"]
    end
    
    subgraph "Compilation Phase"
        K["Compile .c files"]
        L["Compile .cpp files"] 
        M["Compile .adb/.ads files"]
        N["Ada binding generation"]
        O["Link final target"]
    end
    
    subgraph "Output Generation"
        P["Generate .elf"]
        Q["Generate .objdump"]
        R["Generate .readelf"]
        S["Generate library (.a)"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    J --> L
    J --> M
    K --> O
    L --> O
    M --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
    O --> S
```

**Sources:** [corepdk/ubs/src/ubs/ubs-rules.mk:18](), [corepdk/ubs/src/ubs/ubs-post-config.mk:21-98]()

## Multi-Language Compilation Support

UBS provides unified compilation rules for C, C++, and Ada with automatic dependency management and cross-language integration.

### Language-Specific Build Rules

| Language | Source Extension | Object Pattern | Compiler Variable | Flags Variable |
|----------|------------------|----------------|-------------------|----------------|
| C | `.c` | `%.c.o` | `UBS_CC` | `UBS_CC_FLAGS` |
| C++ | `.cpp` | `%.cpp.o` | `UBS_CXX` | `UBS_CXX_FLAGS` |
| Ada Body | `.adb` | `%.o` + `%.ali` | `UBS_ADA` | `UBS_ADA_FLAGS` |
| Ada Spec | `.ads` | `%.o` + `%.ali` | `UBS_ADA` | `UBS_ADA_FLAGS` |
| Assembly | `.S` | `%.S.o` | `UBS_CC` | `UBS_CC_FLAGS` |

**Sources:** [corepdk/ubs/src/ubs/ubs-rules.mk:69-89]()

### Compilation Rule Implementation

The build system uses template-based compilation rules with automatic dependency generation:

```mermaid
graph LR
    subgraph "Template System"
        TEMPLATE["ubs-compile-tag-flags<br/>Generic compilation template"]
        CCTEMPLATE["ubs-compile CC<br/>C compilation"]
        CXXTEMPLATE["ubs-compile CXX<br/>C++ compilation"]
        ADATEMPLATE["ubs-compile ADA<br/>Ada compilation"]
    end
    
    subgraph "Dependency Generation"
        DEPFLAGS["UBS_DEP_FLAGS<br/>Dependency flags"]
        ADPADEP["ubs-adadep<br/>Ada dependency parser"]
        DEPFILES["*.o.d<br/>Dependency files"]
    end
    
    subgraph "File Processing"
        CSRC["*.c files"]
        CXXSRC["*.cpp files"] 
        ADASRC["*.adb/*.ads files"]
        COBJ["*.c.o objects"]
        CXXOBJ["*.cpp.o objects"]
        ADAOBJ["*.o + *.ali objects"]
    end
    
    TEMPLATE --> CCTEMPLATE
    TEMPLATE --> CXXTEMPLATE  
    TEMPLATE --> ADATEMPLATE
    
    CCTEMPLATE --> DEPFLAGS
    CXXTEMPLATE --> DEPFLAGS
    ADATEMPLATE --> ADPADEP
    
    CSRC --> CCTEMPLATE --> COBJ
    CXXSRC --> CXXTEMPLATE --> CXXOBJ
    ADASRC --> ADATEMPLATE --> ADAOBJ
    
    DEPFLAGS --> DEPFILES
    ADPADEP --> DEPFILES
```

**Sources:** [corepdk/ubs/src/ubs/ubs-rules.mk:37-57](), [corepdk/ubs/src/ubs/ubs-rules.mk:77-89]()

## Global Defines and Code Generation

UBS implements a sophisticated code generation system that creates language-specific constant definitions from makefile variables.

### Global Defines System Architecture

```mermaid
graph TB
    subgraph "Input Variables"
        GDVARS["GD_* variables<br/>Global defines"]
        FEATVARS["FEATURE_* variables<br/>Feature flags"]
    end
    
    subgraph "Python Code Generator"
        UBSPYTHON["ubs_global_defines.py<br/>Code generation engine"]
        EXPAND["_ubs_expand_var()<br/>Variable expansion"]
        FEATEXPAND["_ubs_expand_feature()<br/>Feature processing"]
        WRITECHANGED["write_if_changed()<br/>Incremental updates"]
    end
    
    subgraph "Generated Files"
        ADADEF["ubs.def<br/>Ada preprocessor"]
        ADALIST["ubs-global-defines.def<br/>Ada constants"]
        ADAFEATS["ubs-features.ads<br/>Ada features package"]
        CPPDEF["ubs-global-defines.h<br/>C/C++ defines"]
        CPPFEATS["ubs-features.h<br/>C/C++ features"]
    end
    
    subgraph "Compiler Integration"
        ADAFLAGS["UBS_ADA_FLAGS<br/>-gnatep inclusion"]
        CCFLAGS["UBS_CC_FLAGS<br/>--include directives"]
        CXXFLAGS["UBS_CXX_FLAGS<br/>--include directives"]
    end
    
    GDVARS --> UBSPYTHON
    FEATVARS --> UBSPYTHON
    UBSPYTHON --> EXPAND
    UBSPYTHON --> FEATEXPAND
    UBSPYTHON --> WRITECHANGED
    
    WRITECHANGED --> ADADEF
    WRITECHANGED --> ADALIST
    WRITECHANGED --> ADAFEATS
    WRITECHANGED --> CPPDEF
    WRITECHANGED --> CPPFEATS
    
    ADADEF --> ADAFLAGS
    CPPDEF --> CCFLAGS
    CPPFEATS --> CCFLAGS
    CPPDEF --> CXXFLAGS
    CPPFEATS --> CXXFLAGS
```

**Sources:** [corepdk/ubs/src/ubs/ubs_global_defines.py:79-170](), [corepdk/ubs/src/ubs/ubs-post-config.mk:94-98]()

### Feature Flag Generation Example

The system automatically generates language-appropriate feature flag definitions:

| Input Makefile Variable | Ada Output | C Output | C++ Output |
|-------------------------|------------|-----------|-------------|
| `FEATURE_USB := 1` | `Ubs.Features.USB : constant boolean := True;` | `#define UBS_FEATURES_USB 1` | `constexpr auto USB = 1;` |
| `FEATURE_LOGGING := 0` | `Ubs.Features.LOGGING : constant boolean := False;` | `#define UBS_FEATURES_LOGGING 0` | `constexpr auto LOGGING = 0;` |

**Sources:** [corepdk/ubs/src/ubs/ubs_global_defines.py:114-160]()

## Testing Framework Integration

UBS provides integrated unit testing capabilities with multi-language support and assertion frameworks.

### Test Discovery and Execution

```mermaid
graph TD
    subgraph "Test File Discovery"
        TESTPATTERN["*_unittest.cpp<br/>*_unittest.c<br/>*_selftest.adb"]
        TESTFILTER["UBS_UNITTEST_SUFFIX<br/>_unittest pattern matching"]
        TESTFILES["UBS_UNITTEST_TEST_FILES<br/>Discovered test sources"]
    end
    
    subgraph "Test Compilation"
        UNITTESTOBJ["*_unittest.cpp.o<br/>Special compilation rule"]
        UNITFLAGS["UBS_CXX_FLAGS<br/>Unit test flags"]
        ADATESTGEN["Generated .ads files<br/>Ada test dependencies"]
    end
    
    subgraph "Test Execution Framework"
        UBSTEST["UBS_TEST macros<br/>Test definition"]
        ENSURE["ensure::is_eq<br/>Assertion framework"]
        SELFTEST["selftest_* functions<br/>Self-test entry points"]
    end
    
    subgraph "Test Results"
        UNITTEST["make unittest<br/>Test execution"]
        COVERAGE["make coverage<br/>Coverage analysis"]
        REPORTS["Test reports<br/>Coverage reports"]
    end
    
    TESTPATTERN --> TESTFILTER
    TESTFILTER --> TESTFILES
    TESTFILES --> UNITTESTOBJ
    UNITTESTOBJ --> UNITFLAGS
    TESTFILES --> ADATESTGEN
    
    UNITTESTOBJ --> UBSTEST
    UBSTEST --> ENSURE
    UBSTEST --> SELFTEST
    
    SELFTEST --> UNITTEST
    UNITTEST --> COVERAGE
    COVERAGE --> REPORTS
```

**Sources:** [corepdk/ubs/src/ubs/ubs-rules.mk:62-67](), [corepdk/ubs/src/ubs/ubs-unittest.mk]()

## Platform Abstraction Layer

UBS supports multiple target platforms through a plugin-based platform abstraction system.

### Platform Configuration Structure

```mermaid
graph LR
    subgraph "Platform Detection"
        PLATVAR["UBS_PLATFORM variable<br/>x86, mcxn547, mcxn236"]
        PLATPATHS["UBS_PATH_PLATFORMS<br/>Platform search paths"]
        PLATFILE["Platform .mk file<br/>Platform-specific config"]
    end
    
    subgraph "Toolchain Setup"
        LANGVARS["CC, CXX, ADA, BIND<br/>Compiler variables"]
        LANGCHECK["ubs-lang-check<br/>Executable validation"]
        UBSTOOLS["UBS_CC, UBS_CXX<br/>Validated tool paths"]
    end
    
    subgraph "Platform-Specific Settings"
        FLAGS["CC_FLAGS, CXX_FLAGS<br/>Platform compiler flags"]
        LIBS["Platform libraries"]
        LINKER["Linker scripts<br/>Memory layouts"]
    end
    
    PLATVAR --> PLATPATHS
    PLATPATHS --> PLATFILE
    PLATFILE --> LANGVARS
    LANGVARS --> LANGCHECK
    LANGCHECK --> UBSTOOLS
    
    PLATFILE --> FLAGS
    PLATFILE --> LIBS
    PLATFILE --> LINKER
```

**Sources:** [corepdk/ubs/src/ubs/ubs-platform.mk:18-32](), [corepdk/ubs/src/ubs/ubs-config.mk:35-38]()

### Supported Language Toolchains

The platform layer validates and configures toolchains for all supported languages:

| Language | Variable | Validation Function | Purpose |
|----------|----------|-------------------|---------|
| C | `CC` | `ubs-lang-check` | C compiler (gcc, clang) |
| C++ | `CXX` | `ubs-lang-check` | C++ compiler (g++, clang++) |
| Ada | `ADA` | `ubs-lang-check` | Ada compiler (gnat) |
| Binding | `BIND` | `ubs-lang-check` | Ada binder (gnatbind) |
| Preprocessor | `CPP` | `ubs-lang-check` | C preprocessor |
| Linker | `LD` | `ubs-lang-check` | Linker (ld, gold) |
| Final Link | `LINK` | `ubs-lang-check` | Final linking tool |

**Sources:** [corepdk/ubs/src/ubs/ubs-platform.mk:20-31]()

## Plugin System Architecture

UBS implements an extensible plugin system that allows projects to add custom build commands and functionality.

### Plugin Loading Mechanism

```mermaid
graph TD
    subgraph "Plugin Discovery"
        PLUGINPATHS["etc/plugins/<br/>corepdk_etc/mk/plugins/<br/>Plugin search directories"]
        PLUGINFILES["*.mk files<br/>Makefile plugins"]
        PLUGINLOADER["ubs_include_plugins<br/>Dynamic inclusion"]
    end
    
    subgraph "Plugin Integration"
        COMMANDS["UBS_COMMANDS<br/>Command registry"]
        RESULTS["UBS_COMMANDS_RESULT<br/>Commands with pass/fail"]
        NORESULTS["UBS_COMMANDS_NO_RESULT<br/>Info commands"]
    end
    
    subgraph "Example Plugins"
        LSPLUGIN["ubs-ls.mk<br/>Listing commands"]
        LSCOMMANDS["ls, files commands<br/>Project/file listing"]
        CUSTOMCMDS["Custom build commands<br/>Project-specific extensions"]
    end
    
    PLUGINPATHS --> PLUGINFILES
    PLUGINFILES --> PLUGINLOADER
    PLUGINLOADER --> COMMANDS
    
    COMMANDS --> RESULTS
    COMMANDS --> NORESULTS
    
    PLUGINLOADER --> LSPLUGIN
    LSPLUGIN --> LSCOMMANDS
    PLUGINLOADER --> CUSTOMCMDS
```

**Sources:** [corepdk/ubs/src/ubs/ubs-plugin.mk:18-38](), [corepdk/ubs/src/selftests/projects/x86-ada/etc/plugins/ubs-ls.mk:18-34]()

## Build Artifacts and Output Structure

UBS organizes build outputs in a structured directory hierarchy with support for multiple configurations.

### Output Directory Structure

| Path Pattern | Purpose | Contents |
|--------------|---------|----------|
| `build/{PROJECT}-{PLATFORM}-{MODE}/` | Root build directory | All build artifacts |
| `build/{PROJECT}-{PLATFORM}-{MODE}/obj/` | Object files | `.o`, `.ali`, `.d` files |
| `build/{PROJECT}-{PLATFORM}-{MODE}/gen/` | Generated code | Auto-generated sources |
| `build/{PROJECT}-{PLATFORM}-{MODE}/reports/` | Analysis reports | Coverage, static analysis |
| `build/{PROJECT}-{PLATFORM}-{MODE}/libs/` | Library outputs | `.a` library files |

**Sources:** [corepdk/ubs/src/ubs/ubs-config.mk:44-49]()

### Target Generation Process

```mermaid
graph TD
    subgraph "Object Generation"
        SOURCES["Source files<br/>C/C++/Ada/ASM"]
        OBJECTS["UBS_OBJECTS<br/>Compiled object files"]
        ADABINDER["Ada binder<br/>b__project.adb/o"]
    end
    
    subgraph "Linking Phase"  
        LINKERSCRIPT["Linker script<br/>Memory layout"]
        LIBS["Static libraries<br/>UBS_LIBS_AS"]
        LINKFLAGS["Link flags<br/>UBS_LINK_FLAGS"]
        TARGET["Final executable<br/>UBS_TARGET.elf"]
    end
    
    subgraph "Post-Processing"
        OBJDUMP["Disassembly<br/>.objdump file"]
        READELF["ELF analysis<br/>.readelf file"]
        LIBRARY["Static library<br/>.a file"]
    end
    
    SOURCES --> OBJECTS
    OBJECTS --> ADABINDER
    ADABINDER --> TARGET
    
    LINKERSCRIPT --> TARGET
    LIBS --> TARGET
    LINKFLAGS --> TARGET
    
    TARGET --> OBJDUMP
    TARGET --> READELF
    OBJECTS --> LIBRARY
```

**Sources:** [corepdk/ubs/src/ubs/ubs-rules.mk:24-35](), [corepdk/ubs/src/ubs/ubs-rules.mk:104-111]()

## CI/CD Pipeline

The project utilizes GitLab CI for automated build and test verification. The pipeline is defined to trigger on merge requests, main branch updates, and tags.

### Pipeline Configuration

The `.gitlab-ci.yml` file defines a build matrix for key projects and platforms:

| Project | Platform | Board | Mode |
|---------|----------|-------|------|
| `mcxn547helloworld` | `mcxn556-both` | `mcxn547helloworld` | `rel` |
| `p3957_cxx` | `mcxn556-core0` | `p3957_cxx` | `rel` |

**Sources:** [.gitlab-ci.yml:18-27]()

### Environment and Tooling

The CI environment is provisioned via a Docker image `${CI_REGISTRY_IMAGE}/env:latest`. It includes:
- **Toolchains**: Arm GNU Toolchain (14.2.rel1), GNAT for ARM (14.2.1), and legacy GCC ARM (10.3).
- **SDKs**: NXP MCXN556S SDK (25.09.00), patched during the `before_script` phase.
- **Python Dependencies**: `spsdk` (3.4.0) for firmware signing and manipulation.

**Sources:** [.gitlab-ci.yml:32-51](), [README.md:30-45]()

### Build Orchestration

The `mcu_build.sh` script serves as the primary entry point for both CI and local builds, wrapping the UBS `make` calls with appropriate project and board parameters.

```bash
./mcu_build.sh PROJECT=${PROJECT} BOARD=${BOARD} PLATFORM=${PLATFORM} MODE=${MODE} RUN_LOCAL=1 BUILD_ONLY=1
```

**Sources:** [.gitlab-ci.yml:56](), [README.md:59]()

---

