<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/mods-kernel-driver · page 2 IOCTL Interface · fetched 2026-10-26 -->

# IOCTL Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [mods.h](mods.h)
- [mods_internal.h](mods_internal.h)
- [mods_krnl.c](mods_krnl.c)

</details>



The IOCTL (Input/Output Control) interface is the primary method for userspace applications to interact with the MODS kernel driver. It provides a comprehensive set of operations for accessing hardware resources, managing memory, controlling PCI devices, handling interrupts, and performing platform-specific functions.

## Interface Overview

The MODS driver exposes a character device (`/dev/mods`) through which applications issue IOCTL commands. Each command is identified by a unique code and takes a command-specific data structure as an argument.

```mermaid
flowchart TD
    subgraph "User Space"
        UserApp["User Application"]
        
        subgraph "IOCTL Command Flow"
            Open["open('/dev/mods')"]
            Ioctl["ioctl(fd, cmd, argp)"]
            Close["close(fd)"]
        end
    end
    
    subgraph "Kernel Space"
        Dev["/dev/mods Device"]
        Dispatch["mods_krnl_ioctl()"]
        
        subgraph "Command Handlers"
            MemCmd["Memory Commands\nesc_mods_alloc_pages, etc."]
            PciCmd["PCI Commands\nesc_mods_find_pci_dev, etc."]
            IrqCmd["IRQ Commands\nesc_mods_register_irq, etc."]
            AcpiCmd["ACPI Commands\nesc_mods_eval_acpi_method, etc."]
            PlatCmd["Platform Commands"]
        end
        
        ClientMgr["Client Management"]
        TokenMgr["Access Token Management"]
    end
    
    UserApp --> Open
    Open --> Dev
    UserApp --> Ioctl
    Ioctl --> Dev
    UserApp --> Close
    Close --> Dev
    
    Dev --> Dispatch
    Dispatch --> ClientMgr
    Dispatch --> TokenMgr
    Dispatch --> MemCmd
    Dispatch --> PciCmd
    Dispatch --> IrqCmd
    Dispatch --> AcpiCmd
    Dispatch --> PlatCmd
```

Sources: [mods_krnl.c:19-44](), [mods_krnl.c:2019-2115]()

## Client and Access Management

### Client Management

The MODS driver supports multiple client connections through a client management system that tracks resources per client. Each client is identified by a unique ID assigned when the device is opened.

```mermaid
flowchart LR
    subgraph "Client Management"
        Open["open()"]
        Close["close()"]
        ClientAlloc["alloc_client()"]
        ClientStruct["struct mods_client"]
        FreeClient["free_client()"]
    end
    
    Open --> ClientAlloc
    ClientAlloc --> ClientStruct
    ClientStruct --> |"contains client resources"| ClientStruct
    Close --> FreeClient
    FreeClient --> |"releases resources"| ClientStruct
```

Sources: [mods_krnl.c:431-475](), [mods_krnl.c:477-500](), [mods_internal.h:82-110]()

### Access Token Management

To control concurrent access, the driver implements an access token system. The first client can acquire a token, and subsequent clients must verify this token to use the driver.

```mermaid
flowchart TD
    subgraph "Access Token Flow"
        Acquire["MODS_ESC_ACQUIRE_ACCESS_TOKEN"]
        Verify["MODS_ESC_VERIFY_ACCESS_TOKEN"]
        Release["MODS_ESC_RELEASE_ACCESS_TOKEN"]
    end
    
    Client1["Client 1"] --> Acquire
    Acquire --> |"generates token"| Token["Access Token"]
    Client2["Client 2"] --> Verify
    Verify --> |"validates against"| Token
    Client1 --> Release
    Release --> |"invalidates"| Token
```

Sources: [mods.h:26-59](), [mods_krnl.c:1706-1777]()

## IOCTL Command Processing

The driver processes IOCTL commands through the `mods_krnl_ioctl()` function, which handles parameter validation, copying data between user and kernel space, and dispatching to appropriate handler functions.

```mermaid
sequenceDiagram
    participant App as User Application
    participant Kernel as Linux Kernel
    participant Ioctl as mods_krnl_ioctl()
    participant Handler as Command Handler
    
    App->>Kernel: ioctl(fd, cmd, argp)
    Kernel->>Ioctl: call with cmd and args
    Ioctl->>Ioctl: validate client
    Ioctl->>Ioctl: check access token
    Ioctl->>Ioctl: copy_from_user(arg_copy, arg, arg_size)
    Ioctl->>Handler: call specific handler
    Handler->>Ioctl: return result
    Ioctl->>Ioctl: copy_to_user(arg, arg_copy, arg_size)
    Ioctl->>Kernel: return status
    Kernel->>App: return status
```

Sources: [mods_krnl.c:2019-2115](), [mods_krnl.c:2086-2114]()

## IOCTL Command Categories

The MODS driver supports over 100 IOCTL commands, organized into several functional categories:

### Memory Management Commands

Commands for allocating, freeing, and managing system memory for hardware access.

| Command | Purpose | Key Structure |
|---------|---------|--------------|
| MODS_ESC_ALLOC_PAGES_2 | Allocate system memory | MODS_ALLOC_PAGES_2 |
| MODS_ESC_FREE_PAGES | Free allocated memory | MODS_FREE_PAGES |
| MODS_ESC_GET_PHYSICAL_ADDRESS_2 | Get physical address of allocation | MODS_GET_PHYSICAL_ADDRESS_3 |
| MODS_ESC_DMA_MAP_MEMORY | Map memory to device via IOMMU | MODS_DMA_MAP_MEMORY |
| MODS_ESC_SET_MEMORY_TYPE | Set memory caching attributes | MODS_MEMORY_TYPE |

Sources: [mods.h:75-204](), [mods.h:2022-2204]()

### PCI Management Commands

Commands for discovering, configuring, and accessing PCI devices.

| Command | Purpose | Key Structure |
|---------|---------|--------------|
| MODS_ESC_FIND_PCI_DEVICE_2 | Find PCI device by vendor/device ID | MODS_FIND_PCI_DEVICE_2 |
| MODS_ESC_PCI_READ_2 | Read from PCI config space | MODS_PCI_READ_2 |
| MODS_ESC_PCI_WRITE_2 | Write to PCI config space | MODS_PCI_WRITE_2 |
| MODS_ESC_PCI_GET_BAR_INFO_2 | Get PCI BAR information | MODS_PCI_GET_BAR_INFO_2 |
| MODS_ESC_PCI_BUS_RESCAN | Initiate PCI bus rescan | MODS_PCI_BUS_RESCAN |

Sources: [mods.h:404-613](), [mods.h:2106-2202]()

### Interrupt Handling Commands

Commands for registering, querying, and handling hardware interrupts.

| Command | Purpose | Key Structure |
|---------|---------|--------------|
| MODS_ESC_REGISTER_IRQ_4 | Register for interrupt notification | MODS_REGISTER_IRQ_4 |
| MODS_ESC_UNREGISTER_IRQ_2 | Unregister interrupt notification | MODS_REGISTER_IRQ_2 |
| MODS_ESC_QUERY_IRQ_3 | Query pending interrupts | MODS_QUERY_IRQ_3 |
| MODS_ESC_IRQ_HANDLED_2 | Indicate interrupt was handled | MODS_REGISTER_IRQ_2 |

Sources: [mods.h:729-935](), [mods.h:2445-2475]()

### ACPI Method Commands

Commands for evaluating ACPI methods and accessing ACPI-related information.

| Command | Purpose | Key Structure |
|---------|---------|--------------|
| MODS_ESC_EVAL_ACPI_METHOD | Evaluate ACPI method | MODS_EVAL_ACPI_METHOD |
| MODS_ESC_EVAL_DEV_ACPI_METHOD_3 | Evaluate ACPI method for PCI device | MODS_EVAL_DEV_ACPI_METHOD_3 |
| MODS_ESC_ACPI_GET_DDC_2 | Get EDID data via ACPI _DDC method | MODS_ACPI_GET_DDC_2 |
| MODS_ESC_GET_ACPI_DEV_CHILDREN | Get ACPI device children | MODS_GET_ACPI_DEV_CHILDREN |

Sources: [mods.h:1033-1163](), [mods.h:2043-2124]()

### Platform-Specific Commands

Commands specific to particular hardware platforms, such as ARM or Tegra.

| Command | Purpose | Key Structure |
|---------|---------|--------------|
| MODS_ESC_ARM_FFA_CMD | ARM FF-A interface commands | MODS_FFA_PARAMS |
| MODS_ESC_GET_CLOCK_HANDLE | Get Tegra clock handle | MODS_GET_CLOCK_HANDLE |
| MODS_ESC_BPMP_SET_PCIE_STATE | Set PCIe state via BPMP | MODS_SET_PCIE_STATE |
| MODS_ESC_FLUSH_CPU_CACHE_RANGE | Flush CPU cache on ARM | MODS_FLUSH_CPU_CACHE_RANGE |

Sources: [mods.h:328-338](), [mods.h:425-439](), [mods.h:1439-1502](), [mods.h:1897-1905]()

## Client Data Structures

The driver maintains per-client data structures to track resources and state.

```mermaid
classDiagram
    class mods_client {
        struct list_head irq_list
        struct list_head mem_alloc_list
        struct list_head mem_map_list
        wait_queue_head_t interrupt_event
        struct irq_q_info irq_queue
        spinlock_t irq_lock
        struct mutex mtx
        u32 access_token
        atomic_t num_allocs
        atomic_t num_pages
        u8 client_id
    }
    
    class MODS_MEM_INFO {
        struct list_head list
        struct list_head dma_map_list
        u32 num_pages
        u32 num_chunks
        u8 cache_type
        struct scatterlist *sg
    }
    
    class SYS_MAP_MEMORY {
        struct list_head list
        struct MODS_MEM_INFO *p_mem_info
        struct mods_client *client
        atomic_t usage_count
        phys_addr_t phys_addr
        unsigned long virtual_addr
        unsigned long mapping_length
    }
    
    class dev_irq_map {
        u8 *dev_irq_aperture
        u32 apic_irq
        u8 type
        u8 client_id
        struct pci_dev *dev
        struct list_head list
    }
    
    mods_client "1" --> "*" MODS_MEM_INFO : mem_alloc_list
    mods_client "1" --> "*" SYS_MAP_MEMORY : mem_map_list
    mods_client "1" --> "*" dev_irq_map : irq_list
    SYS_MAP_MEMORY "0..1" --> "1" MODS_MEM_INFO : p_mem_info
```

Sources: [mods_internal.h:82-110](), [mods_internal.h:136-172](), [mods_internal.h:173-186](), [mods_internal.h:290-309]()

## Memory Mapping Interface

In addition to IOCTL commands, the driver supports memory mapping through the `mmap()` system call, allowing direct access to allocated memory or device regions.

```mermaid
sequenceDiagram
    participant App as User Application
    participant Kernel as Linux Kernel
    participant Mmap as mods_krnl_mmap()
    participant MapInternal as map_internal()
    
    App->>Kernel: mmap(fd, addr, length, prot, flags, offset)
    Kernel->>Mmap: call with vm_area_struct
    Mmap->>Mmap: validate client and token
    Mmap->>Mmap: allocate SYS_MAP_MEMORY
    Mmap->>MapInternal: call with client and vma
    MapInternal->>MapInternal: find memory allocation
    alt System memory
        MapInternal->>MapInternal: map_system_mem()
    else Device memory
        MapInternal->>MapInternal: map_device_mem()
    end
    MapInternal->>MapInternal: register_mapping()
    MapInternal->>Mmap: return status
    Mmap->>Kernel: return status
    Kernel->>App: return mapped address
```

Sources: [mods_krnl.c:887-1061](), [mods_krnl.c:1184-1391]()

## Example IOCTL Command Flow

Below is a detailed example of how a memory allocation IOCTL flows through the system:

```mermaid
flowchart TD
    subgraph "User Space"
        App["Application"]
        IOCTL["ioctl(fd, MODS_ESC_ALLOC_PAGES_2, &alloc_params)"]
    end
    
    subgraph "Kernel Space"
        KrnlIOCTL["mods_krnl_ioctl()"]
        ESCAlloc["esc_mods_alloc_pages_2()"]
        AllocPages["mods_alloc_pages()"]
        
        subgraph "Memory Management"
            PageAlloc["__get_free_pages()"]
            CacheConfig["SET_MEMORY_UC/WC"]
            MemTracking["Add to client->mem_alloc_list"]
        end
    end
    
    App --> IOCTL
    IOCTL --> KrnlIOCTL
    KrnlIOCTL --> ESCAlloc
    ESCAlloc --> AllocPages
    AllocPages --> PageAlloc
    AllocPages --> CacheConfig
    AllocPages --> MemTracking
    MemTracking --> |"Returns memory_handle"| ESCAlloc
    ESCAlloc --> |"Returns status"| KrnlIOCTL
    KrnlIOCTL --> |"Returns status"| IOCTL
    IOCTL --> |"memory_handle in alloc_params"| App
```

Sources: [mods_krnl.c:2019-2115](), [mods_krnl.c:2282-2286]()

## Error Handling

The IOCTL interface uses standard Linux error codes to indicate the status of operations. Common error conditions include:

| Error Code | Description | Typical Causes |
|------------|-------------|----------------|
| -EINVAL | Invalid argument | Incorrect parameters, unsupported operation |
| -ENOMEM | Out of memory | Failed memory allocation |
| -ENODEV | No such device | Device not found or not supported |
| -EFAULT | Bad address | Failed to copy data between user and kernel space |
| -EBUSY | Device or resource busy | Resource already in use |
| -EINTR | Interrupted system call | Operation interrupted by signal |

Sources: [mods_krnl.c:2019-2115](), [mods_internal.h:507-591]()

## Security Considerations

The MODS driver provides low-level hardware access and should be used carefully as it can potentially affect system stability. Key security measures include:

1. Access token system to control concurrent access
2. Client resource tracking to prevent leaks
3. Validation of IOCTL parameters
4. Permission checks for sensitive operations

Since the driver provides direct hardware access, it should only be used by trusted applications with appropriate privileges.

Sources: [mods_krnl.c:431-547](), [mods_krnl.c:1706-1777]()

## Conclusion

The IOCTL interface is the primary method for interacting with the MODS kernel driver, providing a comprehensive set of commands for hardware access and management. Understanding this interface is essential for developing applications that need low-level access to NVIDIA hardware for debugging, diagnostics, or development purposes.

For more details on specific subsystems, refer to:
- Memory Management IOCTLs [Memory Management IOCTLs](#2.1)
- PCI Management IOCTLs [PCI Management IOCTLs](#2.2)
- Interrupt Handling IOCTLs [Interrupt Handling IOCTLs](#2.3)
- ACPI Method IOCTLs [ACPI Method IOCTLs](#2.4)

---

