<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-tools · page 3 Package Management · fetched 2026-10-26 -->

# Package Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configure.ac](configure.ac)
- [mirrors/europe/packages.termux.dev](mirrors/europe/packages.termux.dev)
- [mirrors/europe/termux.cdn.lumito.net](mirrors/europe/termux.cdn.lumito.net)
- [mirrors/north_america/mirror.quantum5.ca](mirrors/north_america/mirror.quantum5.ca)
- [scripts/pkg.in](scripts/pkg.in)
- [scripts/termux-change-repo.in](scripts/termux-change-repo.in)

</details>



## Purpose and Scope

This document provides an overview of Termux's package management system, centered around the `pkg` command. The `pkg` utility serves as a unified wrapper that abstracts the underlying package manager (either `apt` or `pacman`), providing a consistent command interface regardless of which backend is configured. It integrates tightly with the mirror infrastructure to ensure reliable package downloads through intelligent mirror selection and health checking.

For detailed information about specific `pkg` subcommands and their options, see [pkg Command Reference](#3.1). For the technical details of mirror selection algorithms and caching strategies, see [Mirror Selection Algorithm](#3.2). For the interactive mirror configuration tool, see [termux-change-repo](#3.3). For information about the mirror infrastructure itself, see [Mirror Infrastructure](#2).

## Architecture Overview

The package management system consists of three primary components that work together to provide package installation, updates, and repository management:

```mermaid
graph TB
    subgraph "User Interface Layer"
        User["User Commands"]
        PkgScript["pkg script<br/>(scripts/pkg.in)"]
        ChangeRepo["termux-change-repo<br/>(scripts/termux-change-repo.in)"]
    end
    
    subgraph "Configuration Layer"
        PackageMgrSetup["termux-setup-package-manager"]
        TermuxAppPkgMgr["TERMUX_APP_PACKAGE_MANAGER<br/>variable"]
        ChosenMirrors["chosen_mirrors symlink<br/>(@TERMUX_PREFIX@/etc/termux/chosen_mirrors)"]
        MirrorFiles["Mirror configuration files<br/>(@TERMUX_PREFIX@/etc/termux/mirrors)"]
    end
    
    subgraph "Mirror Selection Logic"
        SelectMirror["select_mirror()<br/>(scripts/pkg.in:189-394)"]
        CheckMirror["check_mirror()<br/>(scripts/pkg.in:68-79)"]
        GetMirrorUrl["get_mirror_url()<br/>(scripts/pkg.in:138-181)"]
    end
    
    subgraph "Backend Package Managers"
        APT["apt<br/>(Debian packages)"]
        Pacman["pacman<br/>(Arch packages)"]
    end
    
    subgraph "APT Integration"
        SourcesList["sources.list.d/<br/>main.sources, x11.sources, root.sources"]
        PkgCache["pkgcache.bin<br/>(@TERMUX_CACHE_DIR@/apt/pkgcache.bin)"]
        UpdateCache["update_apt_cache()<br/>(scripts/pkg.in:396-435)"]
    end
    
    User --> PkgScript
    User --> ChangeRepo
    
    PkgScript --> PackageMgrSetup
    ChangeRepo --> PackageMgrSetup
    PackageMgrSetup --> TermuxAppPkgMgr
    
    PkgScript --> SelectMirror
    ChangeRepo --> ChosenMirrors
    
    SelectMirror --> ChosenMirrors
    SelectMirror --> MirrorFiles
    SelectMirror --> CheckMirror
    SelectMirror --> GetMirrorUrl
    
    CheckMirror --> MirrorFiles
    GetMirrorUrl --> MirrorFiles
    
    SelectMirror --> SourcesList
    
    PkgScript --> UpdateCache
    UpdateCache --> PkgCache
    UpdateCache --> SourcesList
    
    PkgScript --> TermuxAppPkgMgr
    TermuxAppPkgMgr -->|"apt"| APT
    TermuxAppPkgMgr -->|"pacman"| Pacman
    
    APT --> SourcesList
    APT --> PkgCache
```

**Sources:** [scripts/pkg.in:1-489](), [scripts/termux-change-repo.in:1-206](), [configure.ac:64-68]()

The system operates in three layers:

1. **User Interface Layer**: The `pkg` command and `termux-change-repo` provide user-facing interfaces for package operations and mirror configuration.

2. **Configuration Layer**: The `termux-setup-package-manager` script sets the `TERMUX_APP_PACKAGE_MANAGER` variable, which determines whether `apt` or `pacman` is used. The `chosen_mirrors` symlink points to either a single mirror file or a directory of regional mirrors.

3. **Backend Integration**: Based on `TERMUX_APP_PACKAGE_MANAGER`, commands are translated to either `apt` or `pacman` syntax and executed.

## Dual Backend Support

The `pkg` command supports two package management backends, configured at build time via the `TERMUX_PACKAGE_MANAGER` variable in [configure.ac:64-68](). The backend selection is stored in `TERMUX_APP_PACKAGE_MANAGER` and sourced from the `termux-setup-package-manager` script at runtime.

### Backend Detection and Command Translation

```mermaid
graph LR
    subgraph "Command Entry Point"
        CMD["CMD variable<br/>(user input)"]
        PkgScript["pkg script"]
    end
    
    subgraph "Backend Switch"
        CaseAPT["case apt:<br/>(scripts/pkg.in:452-467)"]
        CasePacman["case pacman:<br/>(scripts/pkg.in:468-483)"]
    end
    
    subgraph "Command Patterns"
        InstallCmd["install/add/i*"]
        UpdateCmd["update/upd*"]
        UpgradeCmd["upgrade/up/upg*"]
        SearchCmd["search/se*"]
        RemoveCmd["uninstall/un*/rem*/rm/del*"]
    end
    
    subgraph "APT Commands"
        AptInstall["apt install"]
        AptUpdate["apt update"]
        AptUpgrade["apt full-upgrade"]
        AptSearch["apt search"]
        AptRemove["apt remove"]
    end
    
    subgraph "Pacman Commands"
        PacmanInstall["pacman -Sy --needed"]
        PacmanUpdate["pacman -Sy"]
        PacmanUpgrade["pacman -Syu"]
        PacmanSearch["pacman -Sys"]
        PacmanRemove["pacman -Rcns"]
    end
    
    PkgScript --> CMD
    CMD --> CaseAPT
    CMD --> CasePacman
    
    CaseAPT --> InstallCmd
    CaseAPT --> UpdateCmd
    CaseAPT --> UpgradeCmd
    CaseAPT --> SearchCmd
    CaseAPT --> RemoveCmd
    
    InstallCmd --> AptInstall
    UpdateCmd --> AptUpdate
    UpgradeCmd --> AptUpgrade
    SearchCmd --> AptSearch
    RemoveCmd --> AptRemove
    
    CasePacman --> InstallCmd
    CasePacman --> UpdateCmd
    CasePacman --> UpgradeCmd
    CasePacman --> SearchCmd
    CasePacman --> RemoveCmd
    
    InstallCmd --> PacmanInstall
    UpdateCmd --> PacmanUpdate
    UpgradeCmd --> PacmanUpgrade
    SearchCmd --> PacmanSearch
    RemoveCmd --> PacmanRemove
```

**Sources:** [scripts/pkg.in:451-484](), [configure.ac:64-68]()

The command translation logic uses prefix matching on user input (e.g., `i*` matches `install`, `ins`, `i`) and routes to appropriate backend commands. Key translations include:

| User Command | APT Backend | Pacman Backend |
|--------------|-------------|----------------|
| `install` / `add` / `i*` | `apt install` | `pacman -Sy --needed` |
| `update` / `upd*` | `apt update` | `pacman -Sy` |
| `upgrade` / `up` / `upg*` | `apt update && apt full-upgrade` | `pacman -Syu` |
| `search` / `se*` | `apt search` | `pacman -Sys` |
| `uninstall` / `un*` / `rem*` / `rm` / `del*` | `apt remove` | `pacman -Rcns` |
| `files` / `f*` | `dpkg -L` | `pacman -Ql` |
| `show` / `sh*` / `inf*` | `apt show` | `pacman -Qi` |

**Sources:** [scripts/pkg.in:453-467](), [scripts/pkg.in:469-483]()

## Mirror Integration

The `pkg` command integrates with the mirror infrastructure through the `select_mirror()` function, which performs intelligent mirror selection before operations that require network access.

### Mirror Selection Trigger Points

The `select_mirror()` function is called before specific operations:

```mermaid
graph TD
    subgraph "Commands Requiring Mirror Selection"
        Install["install/add/i*"]
        Search["search/se*"]
        Update["update/upd*"]
        Upgrade["upgrade/up/upg*"]
    end
    
    subgraph "Mirror Selection Process"
        SelectMirror["select_mirror()"]
        CheckCache["Check pkgcache.bin<br/>age < 6 hours?"]
        ForceFlag["--check-mirror<br/>flag set?"]
        TestCurrent["Test current<br/>mirror only"]
        TestAll["Parallel test<br/>up to 10 mirrors"]
        UpdateSources["Update sources.list"]
    end
    
    subgraph "Additional APT Logic"
        UpdateAptCache["update_apt_cache()<br/>(for install/search)"]
        CheckMetadata["Check metadata<br/>files exist"]
        RunAptUpdate["Run apt update<br/>if needed"]
    end
    
    Install --> SelectMirror
    Search --> SelectMirror
    Update --> SelectMirror
    Upgrade --> SelectMirror
    
    SelectMirror --> ForceFlag
    ForceFlag -->|"true"| TestAll
    ForceFlag -->|"false"| CheckCache
    CheckCache -->|"fresh"| TestCurrent
    CheckCache -->|"stale"| TestAll
    
    TestCurrent --> UpdateSources
    TestAll --> UpdateSources
    
    Install --> UpdateAptCache
    Search --> UpdateAptCache
    
    UpdateAptCache --> CheckMetadata
    CheckMetadata --> RunAptUpdate
```

**Sources:** [scripts/pkg.in:456-466](), [scripts/pkg.in:189-394](), [scripts/pkg.in:396-435]()

### Configuration Files and Symlink Mechanism

The mirror selection system uses a symlink-based configuration approach:

| Path | Type | Purpose |
|------|------|---------|
| `@TERMUX_PREFIX@/etc/termux/chosen_mirrors` | symlink | Points to selected mirror(s) |
| `@TERMUX_PREFIX@/etc/termux/mirrors/default` | file | Cloudflare CDN fallback |
| `@TERMUX_PREFIX@/etc/termux/mirrors/asia/` | directory | 14 Asian mirrors |
| `@TERMUX_PREFIX@/etc/termux/mirrors/chinese_mainland/` | directory | 15 Chinese mirrors |
| `@TERMUX_PREFIX@/etc/termux/mirrors/europe/` | directory | 19 European mirrors |
| `@TERMUX_PREFIX@/etc/termux/mirrors/north_america/` | directory | 8 North American mirrors |
| `@TERMUX_PREFIX@/etc/apt/sources.list.d/main.sources` | file | deb822 format APT sources |
| `@TERMUX_PREFIX@/etc/apt/sources.list` | file | Legacy APT sources (fallback) |

**Sources:** [scripts/pkg.in:14](), [scripts/pkg.in:204-218](), [scripts/pkg.in:191-195]()

The `chosen_mirrors` symlink can point to:
- A single mirror file (e.g., `mirrors/europe/packages.termux.dev`)
- A regional directory (e.g., `mirrors/asia/`)
- The special `all` pseudo-directory (all mirrors)

When `chosen_mirrors` is a directory, `select_mirror()` tests all mirrors within it. When it's a file, only that mirror is used (unless forced to check with `--check-mirror`).

## Command Execution Flow

The following sequence diagram illustrates how a typical package installation command flows through the system:

```mermaid
sequenceDiagram
    participant User
    participant pkg_script as "pkg script"
    participant setup_pkg_mgr as "termux-setup-<br/>package-manager"
    participant select_mirror as "select_mirror()"
    participant check_mirror as "check_mirror()"
    participant update_apt_cache as "update_apt_cache()"
    participant apt as "apt/pacman"
    
    User->>pkg_script: pkg install <package>
    
    pkg_script->>setup_pkg_mgr: source script
    setup_pkg_mgr-->>pkg_script: Set TERMUX_APP_PACKAGE_MANAGER
    
    pkg_script->>select_mirror: Call for mirror selection
    
    select_mirror->>select_mirror: Read chosen_mirrors symlink
    select_mirror->>select_mirror: Load mirror files
    
    alt Cache fresh & no --check-mirror
        select_mirror->>check_mirror: Test current mirror
        check_mirror-->>select_mirror: Return status
    else Cache stale or forced
        select_mirror->>check_mirror: Parallel test (up to 10)
        check_mirror-->>select_mirror: Return statuses
        select_mirror->>select_mirror: Build weighted array
        select_mirror->>select_mirror: Random selection
    end
    
    select_mirror->>select_mirror: Update sources.list.d/
    select_mirror-->>pkg_script: Mirror selected
    
    pkg_script->>update_apt_cache: Check if apt update needed
    
    update_apt_cache->>update_apt_cache: Check pkgcache.bin age
    update_apt_cache->>update_apt_cache: Check metadata files
    
    alt Cache needs update
        update_apt_cache->>apt: apt update
        apt-->>update_apt_cache: Updated
    end
    
    update_apt_cache-->>pkg_script: Cache ready
    
    pkg_script->>apt: apt install <package>
    apt-->>User: Package installed
```

**Sources:** [scripts/pkg.in:456](), [scripts/pkg.in:189-394](), [scripts/pkg.in:396-435](), [scripts/pkg.in:68-79]()

Key phases in the execution flow:

1. **Initialization**: Source `termux-setup-package-manager` to set `TERMUX_APP_PACKAGE_MANAGER` [scripts/pkg.in:12]()

2. **Mirror Selection**: Call `select_mirror()` which:
   - Reads `chosen_mirrors` symlink [scripts/pkg.in:204-218]()
   - Validates mirror URLs with `get_mirror_url()` [scripts/pkg.in:138-181]()
   - Tests mirrors using `check_mirror()` with curl [scripts/pkg.in:68-79]()
   - Performs weighted random selection [scripts/pkg.in:329-354]()
   - Updates APT sources files [scripts/pkg.in:368-393]()

3. **Cache Update** (APT only): Call `update_apt_cache()` which:
   - Checks `pkgcache.bin` modification time [scripts/pkg.in:423]()
   - Verifies metadata files exist [scripts/pkg.in:410-420]()
   - Runs `apt update` if cache is stale (>20 minutes) [scripts/pkg.in:432-434]()

4. **Package Operation**: Execute backend command (apt/pacman) [scripts/pkg.in:456]()

## Root Protection

The `pkg` command includes a safety check to prevent execution as root user, which could cause permission and ownership issues in the Termux environment:

**Sources:** [scripts/pkg.in:4-8]()

```bash
if [[ "$(id -u)" == "0" ]]; then
    echo "Error: Cannot run 'pkg' command as root"
    exit 1
fi
```

This check occurs before any package operations, ensuring that all installed packages maintain proper ownership and permissions for the Termux user context.

## Relationship with termux-change-repo

The `termux-change-repo` tool provides an interactive dialog-based interface for configuring which mirrors `pkg` should use. While `pkg` automatically selects mirrors based on the current configuration, `termux-change-repo` allows users to explicitly set their preferences:

```mermaid
graph TB
    subgraph "User Interaction"
        User["User runs<br/>termux-change-repo"]
        DialogUI["dialog TUI"]
    end
    
    subgraph "Selection Options"
        ModeSelect["Mode Selection:<br/>Group or Single"]
        GroupSelect["Geographic Groups:<br/>Asia, Europe, etc."]
        SingleSelect["Individual Mirrors:<br/>59 mirrors"]
    end
    
    subgraph "Configuration Update"
        UnlinkLink["unlink_and_link()<br/>(termux-change-repo.in:15-21)"]
        ChosenMirrors["Update chosen_mirrors<br/>symlink"]
    end
    
    subgraph "Automatic Mirror Check"
        PkgUpdate["pkg --check-mirror update"]
        SelectMirror["select_mirror()"]
        AptUpdate["apt update"]
    end
    
    User --> DialogUI
    DialogUI --> ModeSelect
    
    ModeSelect --> GroupSelect
    ModeSelect --> SingleSelect
    
    GroupSelect --> UnlinkLink
    SingleSelect --> UnlinkLink
    
    UnlinkLink --> ChosenMirrors
    
    ChosenMirrors --> PkgUpdate
    PkgUpdate --> SelectMirror
    SelectMirror --> AptUpdate
```

**Sources:** [scripts/termux-change-repo.in:1-206](), [scripts/termux-change-repo.in:15-21](), [scripts/termux-change-repo.in:204-205]()

After updating the `chosen_mirrors` symlink, `termux-change-repo` automatically invokes `pkg --check-mirror update` [scripts/termux-change-repo.in:204-205]() to force immediate mirror testing and repository metadata refresh. The `--check-mirror` flag bypasses the 6-hour cache check, ensuring the new mirror configuration takes effect immediately [scripts/pkg.in:438-441]().

## Key Features Summary

| Feature | Implementation | Benefit |
|---------|---------------|---------|
| Unified Interface | Command prefix matching | Consistent UX across apt/pacman |
| Intelligent Caching | 6-hour pkgcache.bin threshold | Reduced mirror checks |
| Parallel Health Checks | Up to 10 concurrent curl processes | Fast mirror selection |
| Weighted Selection | WEIGHT variable in mirror files | Load distribution |
| Geographic Grouping | Regional mirror directories | Low-latency access |
| Automatic Fallback | Default mirror (Cloudflare CDN) | High availability |
| Cache Awareness | update_apt_cache() optimization | Minimal network usage |

**Sources:** [scripts/pkg.in:223-236](), [scripts/pkg.in:240-327](), [scripts/pkg.in:329-354](), [mirrors/europe/packages.termux.dev:3]()

For detailed documentation of individual `pkg` subcommands, their options, and usage examples, see [pkg Command Reference](#3.1). For the internal workings of the mirror selection algorithm including the parallel checking implementation, see [Mirror Selection Algorithm](#3.2).

---

