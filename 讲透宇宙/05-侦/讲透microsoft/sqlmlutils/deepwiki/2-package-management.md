<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/sqlmlutils · page 2 Package Management · fetched 2026-10-26 -->

# Package Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yaml](.github/workflows/ci.yaml)
- [R/R/sqlPackage.R](R/R/sqlPackage.R)

</details>



Package Management is the core functionality of sqlmlutils that enables installation, removal, and enumeration of R and Python packages within SQL Server Machine Learning Services environments. This system abstracts SQL Server's External Library DDL operations and provides dependency resolution, scope management, and permission control for both languages.

For information about executing code that uses installed packages, see [Code Execution](#3). For details about the R-specific API reference, see [R Package Reference](#5). For Python-specific implementation details, see [Python Package Reference](#6).

## Overview

The package management system in sqlmlutils enables data scientists and administrators to manage R and Python packages within SQL Server databases. It provides a unified interface for installing packages from repositories (CRAN, PyPI) or local files, managing package scopes, and handling dependencies automatically.

```mermaid
graph TB
    subgraph "Client Environment"
        RC["R Client"]
        PC["Python Client"]
        LP["Local Packages"]
    end
    
    subgraph "Repository Sources"
        CRAN["CRAN Repository"]
        PYPI["PyPI Repository"]
    end
    
    subgraph "sqlmlutils Package Management"
        API["sql_install.packages()<br/>sql_remove.packages()<br/>sql_installed.packages()"]
        DR["Dependency Resolver"]
        PM["Package Manager"]
    end
    
    subgraph "SQL Server Integration"
        CEL["CREATE EXTERNAL LIBRARY"]
        DEL["DROP EXTERNAL LIBRARY"]
        SYS["sys.external_libraries"]
    end
    
    subgraph "Storage Scopes"
        PUB["PUBLIC Scope<br/>MRS_EXTLIB_SHARED_PATH"]
        PRIV["PRIVATE Scope<br/>MRS_EXTLIB_USER_PATH"]
    end
    
    RC --> API
    PC --> API
    LP --> API
    CRAN --> DR
    PYPI --> DR
    
    API --> PM
    DR --> PM
    PM --> CEL
    PM --> DEL
    CEL --> SYS
    DEL --> SYS
    
    SYS --> PUB
    SYS --> PRIV
    
    style API fill:#f9f,stroke:#333,stroke-width:2px
    style PM fill:#bbf,stroke:#333,stroke-width:2px
```

**Package Management System Architecture**

The system operates through SQL Server's External Library functionality, using `CREATE EXTERNAL LIBRARY` and `DROP EXTERNAL LIBRARY` DDL statements to manage packages. All operations are transactional and include comprehensive error handling and dependency resolution.

Sources: [R/R/sqlPackage.R:1-2700]()

## Core Functions

### Primary Package Management APIs

The package management system exposes three primary functions that mirror R's base package management functions:

| Function | Purpose | Scope Support |
|----------|---------|---------------|
| `sql_install.packages` | Install packages from repositories or files | PUBLIC, PRIVATE |
| `sql_remove.packages` | Remove packages with dependency checking | PUBLIC, PRIVATE |
| `sql_installed.packages` | Enumerate installed packages | PUBLIC, PRIVATE, SYSTEM |

```mermaid
graph LR
    subgraph "Package Operations"
        INSTALL["sql_install.packages()"]
        REMOVE["sql_remove.packages()"]
        LIST["sql_installed.packages()"]
    end
    
    subgraph "Core Implementation"
        INSTALL --> sqlInstallPackagesExtLib
        REMOVE --> getDependentPackagesToUninstall
        LIST --> sqlEnumPackages
    end
    
    subgraph "SQL Integration"
        sqlInstallPackagesExtLib --> sqlCreateExternalLibrary
        sqlInstallPackagesExtLib --> sqlAddExtendedProperty
        getDependentPackagesToUninstall --> sqlDropExternalLibrary
        sqlEnumPackages --> sqlRemoteExecuteFun
    end
    
    subgraph "System Tables"
        sqlCreateExternalLibrary --> external_libraries["sys.external_libraries"]
        sqlAddExtendedProperty --> extended_properties["sys.extended_properties"]
        sqlDropExternalLibrary --> external_libraries
    end
```

**Core Package Management Function Flow**

Sources: [R/R/sqlPackage.R:75-117](), [R/R/sqlPackage.R:145-263](), [R/R/sqlPackage.R:37-72]()

## Scope Management

### Package Scopes

The system supports three distinct package scopes that determine accessibility and storage location:

```mermaid
graph TB
    subgraph "Package Scopes"
        PUBLIC["PUBLIC Scope<br/>Shared across all users"]
        PRIVATE["PRIVATE Scope<br/>User-specific packages"]
        SYSTEM["SYSTEM Scope<br/>Base R/Python packages"]
    end
    
    subgraph "Storage Paths"
        PUBLIC --> SHARED["MRS_EXTLIB_SHARED_PATH<br/>Database-wide access"]
        PRIVATE --> USER["MRS_EXTLIB_USER_PATH<br/>User-specific access"]
        SYSTEM --> BASE[".Library<br/>System packages"]
    end
    
    subgraph "Permission Requirements"
        PUBLIC --> DBO["dbo or db_owner role"]
        PRIVATE --> REGULAR["Regular database users"]
        SYSTEM --> READONLY["Read-only access"]
    end
    
    subgraph "Authorization"
        DBO --> AUTH_PUB["AUTHORIZATION dbo"]
        REGULAR --> AUTH_USER["AUTHORIZATION user"]
        READONLY --> NO_AUTH["No authorization"]
    end
```

**Package Scope Architecture and Permissions**

The scope system ensures proper isolation and security while providing flexibility for different deployment scenarios. Public packages are accessible to all users within a database, while private packages are isolated per user.

Sources: [R/R/sqlPackage.R:657-717](), [R/R/sqlPackage.R:929-989]()

### Scope Resolution Logic

The system automatically determines appropriate scopes and permissions based on user roles:

```mermaid
flowchart TD
    START["Package Installation Request"]
    CHECK_SCOPE{"Scope Parameter"}
    CHECK_USER{"Current User"}
    CHECK_OWNER{"Owner Parameter"}
    
    START --> CHECK_SCOPE
    CHECK_SCOPE -->|PUBLIC| CHECK_USER
    CHECK_SCOPE -->|PRIVATE| PRIVATE_FLOW
    
    CHECK_USER -->|dbo| PUBLIC_DBO["Install as dbo<br/>No AUTHORIZATION"]
    CHECK_USER -->|db_owner| CHECK_OWNER
    CHECK_USER -->|regular user| ERROR_PUB["Error: Permission Denied"]
    
    CHECK_OWNER -->|empty| PUBLIC_DBO
    CHECK_OWNER -->|specified| PUBLIC_AUTH["Install with<br/>AUTHORIZATION owner"]
    
    PRIVATE_FLOW --> CHECK_PRIVATE_USER{"Current User"}
    CHECK_PRIVATE_USER -->|dbo| ERROR_PRIV["Error: dbo cannot use PRIVATE"]
    CHECK_PRIVATE_USER -->|regular user| PRIVATE_USER["Install to user scope<br/>AUTHORIZATION user"]
    
    style ERROR_PUB fill:#ffcccc
    style ERROR_PRIV fill:#ffcccc
    style PUBLIC_DBO fill:#ccffcc
    style PRIVATE_USER fill:#ccffcc
```

**Scope and Permission Resolution Flow**

Sources: [R/R/sqlPackage.R:1435-1517](), [R/R/sqlPackage.R:2188-2220]()

## Package Installation Process

### Installation Workflow

The package installation process involves multiple stages including dependency resolution, downloading, and SQL Server integration:

```mermaid
sequenceDiagram
    participant Client as "sql_install.packages()"
    participant Resolver as "getDependentPackagesToInstall()"
    participant Downloader as "downloadDependentPackages()"
    participant Installer as "sqlHelperInstallPackages()"
    participant SQL as "SQL Server"
    participant Runtime as "External Runtime"
    
    Client->>Resolver: "Resolve dependencies"
    Resolver->>Resolver: "Query available packages"
    Resolver->>Resolver: "Build dependency closure"
    Resolver-->>Client: "Package list with dependencies"
    
    Client->>Downloader: "Download packages"
    Downloader->>Downloader: "Download from CRAN/PyPI"
    Downloader->>Downloader: "Handle binary/source packages"
    Downloader-->>Client: "Local package files"
    
    Client->>Installer: "Install to SQL Server"
    Installer->>SQL: "BEGIN TRANSACTION"
    Installer->>SQL: "CREATE EXTERNAL LIBRARY"
    Installer->>SQL: "sp_addextendedproperty"
    Installer->>Runtime: "sp_execute_external_script"
    Runtime-->>Installer: "Verify installation"
    Installer->>SQL: "COMMIT TRANSACTION"
    Installer-->>Client: "Installation complete"
```

**Package Installation Sequence**

Sources: [R/R/sqlPackage.R:1424-1746](), [R/R/sqlPackage.R:1132-1235](), [R/R/sqlPackage.R:2185-2283]()

### Dependency Resolution

The dependency resolution system builds a complete closure of required packages and handles version conflicts:

```mermaid
graph TB
    subgraph "Input Processing"
        PKGS["Requested Packages"]
        REPOS["Repository URLs"]
        AVAILABLE["available.packages()"]
    end
    
    subgraph "Dependency Analysis"
        DEPS["package_dependencies()"]
        CLOSURE["Dependency Closure"]
        PRUNE["Prune Base Packages"]
    end
    
    subgraph "Conflict Resolution"
        INSTALLED["Installed Packages"]
        COMPARE["Version Comparison"]
        WARNINGS["Version Warnings"]
    end
    
    subgraph "Installation Planning"
        DOWNLOAD["Packages to Download"]
        ATTRIBUTE["Packages to Attribute"]
        SKIP["Packages to Skip"]
    end
    
    PKGS --> DEPS
    REPOS --> AVAILABLE
    AVAILABLE --> DEPS
    DEPS --> CLOSURE
    CLOSURE --> PRUNE
    
    PRUNE --> COMPARE
    INSTALLED --> COMPARE
    COMPARE --> WARNINGS
    COMPARE --> DOWNLOAD
    COMPARE --> ATTRIBUTE
    COMPARE --> SKIP
    
    style CLOSURE fill:#e1f5fe
    style COMPARE fill:#f3e5f5
```

**Dependency Resolution Process**

Sources: [R/R/sqlPackage.R:1132-1235](), [R/R/sqlPackage.R:1242-1316]()

## Package Removal Process

### Removal with Dependency Checking

The package removal system includes sophisticated dependency analysis to prevent breaking dependent packages:

```mermaid
flowchart TD
    START["sql_remove.packages()"]
    VALIDATE["Validate Package Existence"]
    CHECK_DEPS{"dependencies=TRUE"}
    
    START --> VALIDATE
    VALIDATE --> CHECK_DEPS
    
    CHECK_DEPS -->|TRUE| RESOLVE_DEPS["getDependentPackagesToUninstall()"]
    CHECK_DEPS -->|FALSE| DIRECT_REMOVE["Remove Specified Packages Only"]
    
    RESOLVE_DEPS --> FIND_DEPS["Find Package Dependencies"]
    FIND_DEPS --> CHECK_REFS{"checkReferences=TRUE"}
    
    CHECK_REFS -->|TRUE| VERIFY_SAFE["Verify No External References"]
    CHECK_REFS -->|FALSE| FORCE_REMOVE["Force Removal"]
    
    VERIFY_SAFE --> SAFE_LIST["Safe to Remove List"]
    FORCE_REMOVE --> FORCE_LIST["Forced Removal List"]
    DIRECT_REMOVE --> DIRECT_LIST["Direct Removal List"]
    
    SAFE_LIST --> EXECUTE["sqlHelperRemovePackages()"]
    FORCE_LIST --> EXECUTE
    DIRECT_LIST --> EXECUTE
    
    EXECUTE --> DROP_LIB["DROP EXTERNAL LIBRARY"]
    DROP_LIB --> VERIFY_REMOVAL["Verify Removal from Runtime"]
    VERIFY_REMOVAL --> COMPLETE["Removal Complete"]
    
    style VERIFY_SAFE fill:#ccffcc
    style FORCE_REMOVE fill:#ffcccc
```

**Package Removal Flow with Dependency Checking**

Sources: [R/R/sqlPackage.R:2520-2656](), [R/R/sqlPackage.R:2286-2390]()

## External Library Integration

### SQL Server DDL Operations

The system uses SQL Server's External Library DDL statements for all package operations:

```mermaid
graph LR
    subgraph "Package Files"
        ZIP["Package ZIP/TAR"]
        BIN["Binary Content"]
    end
    
    subgraph "SQL DDL Operations"
        CREATE["CREATE EXTERNAL LIBRARY"]
        DROP["DROP EXTERNAL LIBRARY"]
        EXTEND["sp_addextendedproperty"]
    end
    
    subgraph "System Catalogs"
        EXTLIB["sys.external_libraries"]
        EXTPROP["sys.extended_properties"]
        ERRORS["sys.external_library_setup_errors"]
    end
    
    subgraph "Runtime Integration"
        SPEES["sp_execute_external_script"]
        SYNC["Package Synchronization"]
        VERIFY["Installation Verification"]
    end
    
    ZIP --> BIN
    BIN --> CREATE
    CREATE --> EXTLIB
    EXTEND --> EXTPROP
    
    EXTLIB --> SPEES
    SPEES --> SYNC
    SYNC --> VERIFY
    
    DROP --> EXTLIB
    EXTLIB --> ERRORS
```

**SQL Server External Library Integration**

The system reads package files as binary content and creates external libraries with proper authorization. Extended properties track package attributes like top-level installation flags.

Sources: [R/R/sqlPackage.R:1815-1854](), [R/R/sqlPackage.R:1892-1932](), [R/R/sqlPackage.R:1858-1887]()

### Transaction Management

All package operations are wrapped in database transactions to ensure atomicity:

```mermaid
sequenceDiagram
    participant PM as "Package Manager"
    participant DB as "Database Connection"
    participant ExtLib as "External Libraries"
    participant Runtime as "External Runtime"
    
    PM->>DB: "dbBegin()"
    Note over DB: "Start Transaction"
    
    loop For each package
        PM->>ExtLib: "CREATE EXTERNAL LIBRARY"
        PM->>ExtLib: "sp_addextendedproperty"
    end
    
    PM->>Runtime: "sp_execute_external_script"
    Runtime-->>PM: "Verify installation"
    
    alt Success
        PM->>DB: "dbCommit()"
        Note over DB: "Commit Transaction"
    else Error
        PM->>DB: "dbRollback()"
        Note over DB: "Rollback Transaction"
    end
```

**Transaction Management for Package Operations**

Sources: [R/R/sqlPackage.R:2223-2270](), [R/R/sqlPackage.R:2326-2377]()

## Error Handling and Verification

### Installation Verification

The system includes comprehensive verification to ensure packages are properly installed and accessible:

```mermaid
graph TB
    subgraph "Installation Steps"
        CREATE_LIB["CREATE EXTERNAL LIBRARY"]
        ADD_PROP["Add Extended Properties"]
        TRIGGER_SYNC["Trigger Runtime Sync"]
    end
    
    subgraph "Verification Process"
        QUERY_IDS["Query external_library_id"]
        CHECK_ERRORS["Check setup_errors"]
        VERIFY_PATH["Verify in Library Path"]
    end
    
    subgraph "Error Sources"
        DDL_ERRORS["DDL Execution Errors"]
        SETUP_ERRORS["Runtime Setup Errors"]
        PATH_ERRORS["Library Path Errors"]
    end
    
    subgraph "Error Actions"
        ROLLBACK["Transaction Rollback"]
        REPORT["Detailed Error Reporting"]
        CLEANUP["Cleanup Partial State"]
    end
    
    CREATE_LIB --> QUERY_IDS
    ADD_PROP --> CHECK_ERRORS
    TRIGGER_SYNC --> VERIFY_PATH
    
    QUERY_IDS --> SETUP_ERRORS
    CHECK_ERRORS --> SETUP_ERRORS
    VERIFY_PATH --> PATH_ERRORS
    
    DDL_ERRORS --> ROLLBACK
    SETUP_ERRORS --> REPORT
    PATH_ERRORS --> CLEANUP
    
    style SETUP_ERRORS fill:#ffcccc
    style ROLLBACK fill:#ffeeee
```

**Package Installation Verification and Error Handling**

Sources: [R/R/sqlPackage.R:2132-2183](), [R/R/sqlPackage.R:2033-2078](), [R/R/sqlPackage.R:2400-2452]()

## Language-Specific Implementations

### Multi-Language Support Architecture

While this page focuses on the R implementation, the system is designed to support both R and Python packages through a unified interface:

```mermaid
graph TB
    subgraph "Language Abstraction"
        LANG_PARAM["languageName Parameter"]
        SPEES_LANG["@language in sp_execute_external_script"]
        EXTLIB_LANG["language column in sys.external_libraries"]
    end
    
    subgraph "R Implementation"
        R_API["sql_install.packages()"]
        R_REPOS["CRAN Repositories"]
        R_RUNTIME["R External Runtime"]
    end
    
    subgraph "Python Implementation"
        PY_API["SQLPackageManager"]
        PY_REPOS["PyPI Repositories"]
        PY_RUNTIME["Python External Runtime"]
    end
    
    subgraph "Shared Infrastructure"
        COMMON_DDL["External Library DDL"]
        COMMON_SCOPE["Scope Management"]
        COMMON_AUTH["Authorization Logic"]
    end
    
    LANG_PARAM --> SPEES_LANG
    LANG_PARAM --> EXTLIB_LANG
    
    R_API --> COMMON_DDL
    PY_API --> COMMON_DDL
    
    R_REPOS --> R_RUNTIME
    PY_REPOS --> PY_RUNTIME
    
    R_RUNTIME --> COMMON_SCOPE
    PY_RUNTIME --> COMMON_SCOPE
    
    COMMON_DDL --> COMMON_AUTH
    COMMON_SCOPE --> COMMON_AUTH
```

**Multi-Language Package Management Architecture**

The language parameter flows through all operations to ensure proper runtime targeting and package isolation between R and Python environments.

Sources: [R/R/sqlPackage.R:24](), [R/R/sqlPackage.R:481-482](), [R/R/sqlPackage.R:1836]()

---

