<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/remote-media · extra page SMB/CIFS Share Mounting · fetched 2026-10-26 -->

# SMB/CIFS Share Mounting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/smb.hpp](src/smb.hpp)
- [src/state_machine.hpp](src/state_machine.hpp)
- [src/utils.hpp](src/utils.hpp)

</details>



## Purpose and Scope

This document details the SMB/CIFS share mounting implementation in the virtual media service. The `SmbShare` class provides functionality to mount remote CIFS/SMB network shares as local filesystem paths, which can then be served via nbdkit as virtual media devices. This page focuses specifically on the CIFS mounting mechanism. For HTTPS-based image sources, see [HTTPS Image Support](#3.3.2). For the overall state machine orchestration, see [MountPointStateMachine](#3.1).

The SMB/CIFS mounting capability enables the virtual media service to present ISO images or other disk images stored on Windows file shares or Samba servers to the host system as USB mass storage devices.

## The SmbShare Class

The `SmbShare` class encapsulates all SMB/CIFS mounting operations. It is defined in [src/smb.hpp:13-101]() and provides three primary operations:

```mermaid
classDiagram
    class SmbShare {
        -string mountDir
        +SmbShare(mountDir: fs::path)
        +mount(remote: fs::path, rw: bool, credentials: CredentialsProvider*) bool
        +createMountDir(name: fs::path)$ optional~fs::path~
        +unmount(mountDir: fs::path)$ void
    }
    
    class CredentialsProvider {
        +user() string
        +password() string
    }
    
    SmbShare --> CredentialsProvider : uses
    
    note for SmbShare "Static methods for directory lifecycle\nInstance methods for mounting"
```

**Sources:** [src/smb.hpp:13-101]()

### Key Methods

| Method | Type | Purpose |
|--------|------|---------|
| `createMountDir()` | Static | Creates temporary directory in `/tmp` for mounting |
| `mount()` | Instance | Performs CIFS mount with authentication |
| `unmount()` | Static | Unmounts share and removes directory |

## Mount Process

The SMB/CIFS mounting process involves several coordinated steps orchestrated by the `MountPointStateMachine`.

```mermaid
sequenceDiagram
    participant SM as ActivationStartedEvent
    participant SS as SmbShare
    participant FS as Filesystem
    participant Kernel as Linux Kernel
    participant CP as CredentialsProvider
    
    SM->>SS: createMountDir(name)
    SS->>FS: fs::temp_directory_path()
    SS->>FS: fs::create_directory()
    FS-->>SS: /tmp/mount_dir
    SS-->>SM: optional<fs::path>
    
    SM->>SM: Parse imgUrl to get remote path
    SM->>SS: SmbShare(mountDir)
    SM->>SS: mount(remote, rw, credentials)
    
    alt With Credentials
        SS->>CP: user()
        SS->>CP: password()
        CP-->>SS: username, password
    else Guest Access
        SS->>SS: Set guest credentials
    end
    
    SS->>SS: Build mount options
    SS->>Kernel: ::mount(remote, mountDir, "cifs", options)
    Kernel-->>SS: 0 (success)
    
    SS->>SS: secureCleanup(options)
    SS->>SS: secureCleanup(credentialsOpt)
    SS-->>SM: true
    
    SM->>SM: spawn nbdkit with localFile
```

**Sources:** [src/state_machine.hpp:665-704](), [src/smb.hpp:19-58]()

### Creating Mount Directory

The `createMountDir()` static method creates a temporary mount point:

```mermaid
flowchart TD
    A["createMountDir(name)"] --> B["destPath = /tmp/name"]
    B --> C{Directory exists?}
    C -->|Yes| D["unmount(destPath)"]
    C -->|No| E["fs::create_directory(destPath)"]
    D --> E
    E --> F{Success?}
    F -->|Yes| G["return optional<fs::path>"]
    F -->|No| H["Log error"]
    H --> I["return empty optional"]
```

**Sources:** [src/smb.hpp:60-78]()

The mount directory is created under the system's temporary directory (typically `/tmp`) with the mount point name as a subdirectory. If a directory already exists, the method attempts to unmount it first to ensure a clean state.

### Mounting the Share

The `mount()` method performs the actual CIFS mount operation at [src/smb.hpp:19-58](). The process involves:

1. **Building mount options** - Construct the CIFS mount option string
2. **Handling credentials** - Add authentication parameters (guest or user/password)
3. **Invoking system mount** - Call `::mount()` system call
4. **Secure cleanup** - Zero out credential strings from memory

### CIFS Mount Options

The service uses specific CIFS mount options to ensure secure and reliable connections:

```mermaid
graph LR
    A["CIFS Mount Options"] --> B["sec=ntlmsspi"]
    A --> C["seal"]
    A --> D["vers=3.0"]
    A --> E["cache=none"]
    A --> F["ro/rw"]
    A --> G["Credentials"]
    
    B --> B1["NTLM authentication<br/>with extended security"]
    C --> C1["Enable SMB encryption"]
    D --> D1["Force SMB 3.0 protocol"]
    E --> E1["Disable client-side caching"]
    F --> F1["Read-only or read-write"]
    G --> G1["username + password<br/>or guest"]
```

**Sources:** [src/smb.hpp:24-42]()

The complete option string constructed at [src/smb.hpp:24-42]() is:

```
sec=ntlmsspi,seal,vers=3.0,cache=none,{ro|rw},{credentials}
```

| Option | Purpose |
|--------|---------|
| `sec=ntlmsspi` | Use NTLM authentication with extended security (SPNEGO) |
| `seal` | Enable SMB encryption for data transfer |
| `vers=3.0` | Force SMB protocol version 3.0 |
| `cache=none` | Disable client-side caching to ensure data consistency |
| `ro` or `rw` | Mount as read-only or read-write |
| Credentials | Either `guest,username=OpenBmc` or `username=X,password=Y` |

## Credential Handling

Credential security is critical in the SMB mounting process. The system implements multiple layers of protection:

```mermaid
flowchart TD
    A["D-Bus Mount Call"] --> B["Unix FD with credentials"]
    B --> C["Read into buffer"]
    C --> D["Parse user and password"]
    D --> E["CredentialsProvider"]
    E --> F["SmbShare::mount()"]
    F --> G["Build options string"]
    G --> H["::mount() system call"]
    H --> I["secureCleanup(options)"]
    I --> J["secureCleanup(credentialsOpt)"]
    J --> K["CredentialsProvider destroyed"]
    K --> L["explicit_bzero on buffers"]
    
    style I fill:#f9f9f9
    style J fill:#f9f9f9
    style L fill:#f9f9f9
```

**Sources:** [src/state_machine.hpp:448-484](), [src/smb.hpp:29-48](), [src/utils.hpp:19-57]()

### Credential Flow

1. **Reception** - Credentials arrive via Unix file descriptor from D-Bus [src/state_machine.hpp:453-455]()
2. **Parsing** - User and password are extracted from NULL-delimited buffer [src/state_machine.hpp:473-475]()
3. **Encapsulation** - Wrapped in `CredentialsProvider` [src/state_machine.hpp:478-480]()
4. **Usage** - Passed to `SmbShare::mount()` [src/smb.hpp:36-39]()
5. **Cleanup** - All credential strings are zeroed with `explicit_bzero` [src/smb.hpp:47-48]()

### Guest vs Authenticated Mounting

The mount method supports two authentication modes:

```mermaid
graph TD
    A["mount(remote, rw, credentials)"] --> B{credentials present?}
    B -->|No| C["Guest Mode"]
    B -->|Yes| D["Authenticated Mode"]
    
    C --> C1["credentialsOpt =<br/>guest,username=OpenBmc"]
    D --> D1["credentialsOpt =<br/>username=X,password=Y"]
    
    C1 --> E["Build full options string"]
    D1 --> E
    
    E --> F["::mount() call"]
    F --> G["secureCleanup()"]
```

**Sources:** [src/smb.hpp:30-42]()

Guest mounting is used when no credentials are provided [src/smb.hpp:32-33](), while authenticated mounting uses the username and password from the `CredentialsProvider` [src/smb.hpp:37-39]().

## State Machine Integration

The `SmbShare` class is utilized by the `MountPointStateMachine` during the activation process when a CIFS URL is detected.

```mermaid
flowchart LR
    A["ReadyState"] --> B["MountEvent"]
    B --> C["ActivatingState"]
    C --> D["ActivationStartedEvent"]
    D --> E{URL Type?}
    E -->|"smb://"| F["mountSmbShare()"]
    E -->|"https://"| G["mountHttpsShare()"]
    
    F --> H["createMountDir()"]
    H --> I["SmbShare::mount()"]
    I --> J["spawnNbdKit(localFile)"]
    J --> K["WaitingForGadgetState"]
    
    style F fill:#f9f9f9
    style H fill:#f9f9f9
    style I fill:#f9f9f9
```

**Sources:** [src/state_machine.hpp:645-704]()

### URL Parsing and Path Construction

The state machine parses the SMB URL to extract the necessary components:

```mermaid
graph TD
    A["imgUrl: smb://server/share/path/image.iso"] --> B["getImagePath()"]
    B --> C["remote: /share/path/image.iso"]
    C --> D["remoteParent: /share/path"]
    C --> E["filename: image.iso"]
    D --> F["mount(remoteParent)"]
    E --> G["localFile: /tmp/mount_dir/image.iso"]
    F --> H["Mounted at /tmp/mount_dir"]
    H --> G
    G --> I["nbdkit file file=/tmp/mount_dir/image.iso"]
```

**Sources:** [src/state_machine.hpp:675-681](), [src/state_machine.hpp:890-907]()

The URL parsing at [src/state_machine.hpp:879-888]() identifies CIFS URLs by the `smb://` scheme prefix. The path is then split into:
- **remoteParent**: The directory to mount (e.g., `/share/path`)
- **filename**: The image file within the mounted share (e.g., `image.iso`)
- **localFile**: The local path after mounting (e.g., `/tmp/mount_dir/image.iso`)

### Mount Sequence in mountSmbShare

The `mountSmbShare()` method at [src/state_machine.hpp:665-704]() orchestrates the entire mount workflow:

1. **Create mount directory** using `SmbShare::createMountDir()` [src/state_machine.hpp:667-672]()
2. **Parse URL** to extract remote path and filename [src/state_machine.hpp:675-681]()
3. **Mount the share** at remoteParent with credentials [src/state_machine.hpp:683-689]()
4. **Spawn nbdkit** to serve the local file [src/state_machine.hpp:691-697]()
5. **Store mount directory** in target for later cleanup [src/state_machine.hpp:701]()

If any step fails, the method performs appropriate cleanup (e.g., removing the mount directory) and returns to `ReadyState` with an error code.

## Unmount Process

The unmount operation reverses the mount process and ensures complete cleanup.

```mermaid
sequenceDiagram
    participant SM as StateMachine
    participant SS as SmbShare
    participant Kernel as Linux Kernel
    participant FS as Filesystem
    
    SM->>SM: ReadyState::onEnter()
    SM->>SM: Check target->mountDir
    
    alt mountDir exists
        SM->>SS: unmount(mountDir)
        SS->>Kernel: ::umount(mountDir)
        Kernel-->>SS: result
        
        alt umount failed
            SS->>SS: Log error
        end
        
        SS->>FS: fs::remove_all(mountDir)
        
        alt remove failed
            SS->>SS: Log error
        end
        
        SS-->>SM: void
        SM->>SM: target.reset()
    end
```

**Sources:** [src/state_machine.hpp:96-108](), [src/smb.hpp:80-97]()

### Unmount Steps

The unmount process at [src/smb.hpp:80-97]() performs two operations:

1. **System unmount** - Calls `::umount()` to detach the CIFS mount [src/smb.hpp:85-90]()
2. **Directory removal** - Removes the mount directory and all contents [src/smb.hpp:92-96]()

Both operations log errors if they fail but do not throw exceptions, ensuring that cleanup attempts continue even if one step fails.

### Automatic Cleanup

The state machine automatically triggers unmount when transitioning to `ReadyState` at [src/state_machine.hpp:96-108](). This ensures that:
- Mount points are not left orphaned after unmount operations
- Resources are cleaned up when processes fail
- Mount directories are reusable for subsequent mount operations

## Error Handling

The SMB mounting implementation includes error handling at multiple levels:

| Error Condition | Handling | Location |
|----------------|----------|----------|
| Mount directory creation fails | Return empty optional | [src/smb.hpp:70-77]() |
| Mount system call fails | Return false, log errno | [src/smb.hpp:50-55]() |
| Unmount fails | Log error, continue cleanup | [src/smb.hpp:85-90]() |
| Directory removal fails | Log error, continue cleanup | [src/smb.hpp:92-96]() |
| Malformed credentials | Throw SdBusError | [src/state_machine.hpp:467-470]() |
| Mount failed in state machine | Transition to ReadyState with error | [src/state_machine.hpp:686-689]() |

The error handling strategy is:
- **Creation failures** return empty optionals or false to indicate failure
- **Cleanup failures** are logged but don't propagate errors (best-effort cleanup)
- **State machine errors** transition to `ReadyState` with appropriate error codes and messages

**Sources:** [src/smb.hpp:13-101](), [src/state_machine.hpp:665-704]()

---

