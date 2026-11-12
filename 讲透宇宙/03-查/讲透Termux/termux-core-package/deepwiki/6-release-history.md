<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-core-package · page 6 Release History · fetched 2026-10-26 -->

# Release History

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [site/pages/en/projects/releases/0/v0.1.0.md](site/pages/en/projects/releases/0/v0.1.0.md)
- [site/pages/en/projects/releases/0/v0.2.0.md](site/pages/en/projects/releases/0/v0.2.0.md)
- [site/pages/en/projects/releases/0/v0.3.0.md](site/pages/en/projects/releases/0/v0.3.0.md)
- [site/pages/en/projects/releases/index.md](site/pages/en/projects/releases/index.md)

</details>



This page documents the chronological release history of the termux-core-package, including version details, feature additions, changes, bug fixes, and component evolution. For information about build processes and package generation, see [Build System](#2), and for details about the core libraries and utilities, refer to [Core Libraries](#3).

## Release Timeline

The following diagram illustrates the release timeline of the termux-core-package:

```mermaid
gantt
    title Termux Core Package Release Timeline
    dateFormat YYYY-MM-DD
    axisFormat %Y-%m-%d
    
    section Major Releases
    v0.1.0 (Initial Release)     :milestone, m1, 2025-03-21, 0d
    v0.2.0 (Architecture Expansion) :milestone, m2, 2025-03-22, 0d
    v0.3.0 (Feature Enhancements) :milestone, m3, 2025-03-26, 0d
    
    section Development Periods
    Initial Development        :done, dev1, 2025-03-15, 2025-03-21
    v0.1.0 to v0.2.0           :done, dev2, 2025-03-21, 2025-03-22
    v0.2.0 to v0.3.0           :done, dev3, 2025-03-22, 2025-03-26
```

Sources: [site/pages/en/projects/releases/index.md](), [site/pages/en/projects/releases/0/v0.1.0.md](), [site/pages/en/projects/releases/0/v0.2.0.md](), [site/pages/en/projects/releases/0/v0.3.0.md]()

## Version Summary

The following table provides a summary of all releases to date:

| Version | Release Date | Summary | Commit Range |
|---------|--------------|---------|--------------|
| v0.1.0  | 2025-03-21   | Initial release with core libraries, utilities and test framework | c6a3bcd5...v0.1.0 |
| v0.2.0  | 2025-03-22   | Added RISC-V 64-bit architecture support | v0.1.0...v0.2.0 |
| v0.3.0  | 2025-03-26   | Enhanced utilities functionality, standardized version output, fixed bugs | v0.2.0...v0.3.0 |

Sources: [site/pages/en/projects/releases/index.md](), [site/pages/en/projects/releases/0/v0.1.0.md](), [site/pages/en/projects/releases/0/v0.2.0.md](), [site/pages/en/projects/releases/0/v0.3.0.md]()

## Component Evolution

This diagram shows how the key components of the termux-core-package have evolved across releases:

```mermaid
graph TD
    subgraph "v0.1.0 (2025-03-21)"
        A1["Core Libraries:
        - libtermux-core_nos_c_tre
        - libtermux-core_nos_cxx_tre"]
        A2["Utilities:
        - termux-scoped-env-variable
        - termux-apps-info-env-variable
        - termux-apps-info-app-version-name"]
        A3["Testing:
        - termux-core-tests
        - termux-external-packages_tests"]
    end
    
    subgraph "v0.2.0 (2025-03-22)"
        B1["Architecture Support:
        - Added RISC-V 64-bit (riscv64)"]
    end
    
    subgraph "v0.3.0 (2025-03-26)"
        C1["UnixForkUtils:
        - Enhanced forkChild()"]
        C2["UnixShellEnvironment:
        - Added areEmptyVarsInEnv()"]
        C3["UnixFileUtils:
        - Renamed getFdRealpath() to getFdRealPath()
        - Added isFdPath()"]
        C4["Version String:
        - Standardized format"]
        C5["Bug Fixes:
        - Fixed file pointer leak
        - Fixed typos
        - Enhanced test conditionals"]
    end
    
    A1 --> B1
    A2 --> C1
    A2 --> C2
    A2 --> C3
    A2 --> C4
    A3 --> C5
    B1 --> C5
```

Sources: [site/pages/en/projects/releases/0/v0.1.0.md](), [site/pages/en/projects/releases/0/v0.2.0.md](), [site/pages/en/projects/releases/0/v0.3.0.md]()

## Detailed Release Information

### v0.3.0 (2025-03-26)

This is the current latest release of termux-core-package, focusing on enhancing utility functions and fixing bugs.

#### Added

- Enhanced `forkChild()` in UnixForkUtils to support redirecting stdin/stdout/stderr to /dev/null and saving original stdout/stderr
- Added `areEmptyVarsInEnv()` function to UnixShellEnvironment
- Renamed `getFdRealpath()` to `getFdRealPath()` in UnixFileUtils (correcting a typo)
- Added `isFdPath()` function to UnixFileUtils

#### Changed

- Standardized version string output format to `<component_name> version=<name> org=<name> project=<name>`

#### Fixed

- Fixed incorrect errno return in `getRegularFileFdRealPath()` function
- Fixed file pointer leak in `getSeProcessContextFromFile()`
- Improved test execution logic for tudo and sudo tests
- Fixed typo in riscv64 support implementation

**Commit History:** v0.2.0...v0.3.0

Sources: [site/pages/en/projects/releases/0/v0.3.0.md]()

### v0.2.0 (2025-03-22)

This minor release added support for an additional hardware architecture.

#### Added

- Added support for RISC-V 64-bit architecture (riscv64)

**Commit History:** v0.1.0...v0.2.0

Sources: [site/pages/en/projects/releases/0/v0.2.0.md]()

### v0.1.0 (2025-03-21)

The initial release of termux-core-package, establishing the foundation with core libraries, utilities, and testing framework.

#### Added

- Introduced `termux-core-tests` for core testing functionality
- Added `termux-external-packages_tests` for testing external packages
- Established core C and C++ libraries:
  - `libtermux-core_nos_c_tre`
  - `libtermux-core_nos_cxx_tre`
- Created utility scripts:
  - `termux-scoped-env-variable`
  - `termux-apps-info-env-variable`
  - `termux-apps-info-app-version-name`

**Commit History:** c6a3bcd5...v0.1.0

Sources: [site/pages/en/projects/releases/0/v0.1.0.md]()

## Code Entity Relationships

The following diagram maps release components to their specific code entities to help bridge natural language descriptions with actual code implementations:

```mermaid
graph TD
    subgraph "Libraries"
        L1["libtermux-core_nos_c_tre"]
        L2["libtermux-core_nos_cxx_tre"]
    end

    subgraph "Code Components"
        C1["UnixFileUtils:
        - getFdRealPath()
        - isFdPath()
        - getRegularFileFdRealPath()"]
        
        C2["UnixForkUtils:
        - forkChild()"]
        
        C3["UnixShellEnvironment:
        - areEmptyVarsInEnv()"]
        
        C4["UnixSeLinuxUtils:
        - getSeProcessContextFromFile()"]
    end
    
    subgraph "Utilities"
        U1["termux-scoped-env-variable"]
        U2["termux-apps-info-env-variable"]
        U3["termux-apps-info-app-version-name"]
    end
    
    subgraph "Tests"
        T1["termux-core-tests"]
        T2["termux-external-packages_tests"]
    end
    
    subgraph "Release Version Changes"
        R1["v0.1.0: Initial Implementation"]
        R2["v0.2.0: RISC-V Support"]
        R3["v0.3.0: Enhanced Functionality"]
    end
    
    L1 --> C1
    L1 --> C2
    L1 --> C3
    L1 --> C4
    
    L2 --> C1
    L2 --> C2
    L2 --> C3
    L2 --> C4
    
    R1 --> L1
    R1 --> L2
    R1 --> U1
    R1 --> U2
    R1 --> U3
    R1 --> T1
    R1 --> T2
    
    R2 --> L1
    R2 --> L2
    
    R3 --> C1
    R3 --> C2
    R3 --> C3
    R3 --> C4
```

Sources: [site/pages/en/projects/releases/0/v0.1.0.md](), [site/pages/en/projects/releases/0/v0.2.0.md](), [site/pages/en/projects/releases/0/v0.3.0.md]()

## Function Evolution Through Releases

The following diagram illustrates the evolution of specific functions and their capabilities across releases:

```mermaid
graph TD
    subgraph "v0.1.0"
        V1UnixFile["UnixFileUtils"]
        V1UnixFork["UnixForkUtils:
        - Basic forkChild()"]
        V1UnixShell["UnixShellEnvironment"]
        V1UnixSELinux["UnixSeLinuxUtils:
        - getSeProcessContextFromFile() with leak"]
    end
    
    subgraph "v0.2.0"
        V2UnixFile["UnixFileUtils:
        - getFdRealpath() with typo"]
        V2UnixFork["UnixForkUtils:
        - Basic forkChild()"]
        V2UnixShell["UnixShellEnvironment"]
        V2UnixSELinux["UnixSeLinuxUtils:
        - getSeProcessContextFromFile() with leak"]
    end
    
    subgraph "v0.3.0"
        V3UnixFile["UnixFileUtils:
        - getFdRealPath() renamed
        - isFdPath() added
        - Fixed getRegularFileFdRealPath()"]
        V3UnixFork["UnixForkUtils:
        - Enhanced forkChild() with /dev/null redirection"]
        V3UnixShell["UnixShellEnvironment:
        - areEmptyVarsInEnv() added"]
        V3UnixSELinux["UnixSeLinuxUtils:
        - getSeProcessContextFromFile() fixed"]
    end
    
    V1UnixFile --> V2UnixFile
    V1UnixFork --> V2UnixFork
    V1UnixShell --> V2UnixShell
    V1UnixSELinux --> V2UnixSELinux
    
    V2UnixFile --> V3UnixFile
    V2UnixFork --> V3UnixFork
    V2UnixShell --> V3UnixShell
    V2UnixSELinux --> V3UnixSELinux
```

Sources: [site/pages/en/projects/releases/0/v0.1.0.md](), [site/pages/en/projects/releases/0/v0.2.0.md](), [site/pages/en/projects/releases/0/v0.3.0.md]()

## Release Sources

The termux-core-package releases are available from the following sources:

- GitHub Releases: [https://github.com/termux/termux-core-package/releases](https://github.com/termux/termux-core-package/releases)

The release changelogs follow the [Keep a Changelog](https://github.com/olivierlacan/keep-a-changelog) specification format.

Sources: [site/pages/en/projects/releases/index.md]()