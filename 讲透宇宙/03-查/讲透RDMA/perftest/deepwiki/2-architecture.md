<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/perftest · page 2 Architecture · fetched 2026-11-11 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/perftest_communication.c](src/perftest_communication.c)
- [src/perftest_communication.h](src/perftest_communication.h)
- [src/perftest_parameters.c](src/perftest_parameters.c)
- [src/perftest_resources.c](src/perftest_resources.c)

</details>



This document describes the overall system architecture of perftest, a comprehensive toolkit for measuring and benchmarking RDMA (Remote Direct Memory Access) performance. The architecture is designed to support multiple RDMA verbs, connection types, and memory backends while maintaining a clean separation of concerns.

For information about specific test types, see [Test Types](#1.1). For details on building and installing perftest, see [Building and Installation](#6).

## Core Components Overview

The perftest toolkit is built around a modular architecture with several key components that work together to provide flexible and comprehensive RDMA performance measurement capabilities.

```mermaid
graph TD
    subgraph "Core Library Components"
        parameters["perftest_parameters"]
        resources["perftest_resources"]
        communication["perftest_communication"]
        
        parameters --> resources
        communication --> resources
    end
    
    subgraph "Memory Subsystem"
        memory["memory_ctx interface"]
        memory --> |"Default"| host_memory["host_memory.c"]
        memory --> |"Memory Mapped"| mmap_memory["mmap_memory.c"]
        memory -.-> |"Optional"| accelerator_memory["Accelerator Memory<br>(CUDA, ROCm, etc.)"]
    end
    
    subgraph "Test Programs"
        bw_tests["Bandwidth Tests"]
        lat_tests["Latency Tests"]
        raw_eth_tests["Raw Ethernet Tests"]
    end
    
    resources --> memory
    resources --> bw_tests & lat_tests & raw_eth_tests
    parameters --> bw_tests & lat_tests & raw_eth_tests
    communication --> bw_tests & lat_tests & raw_eth_tests
```

Sources: 
- [src/perftest_resources.c:1-45]()
- [src/perftest_parameters.c:1-22]()
- [src/perftest_communication.c:1-25]()

### Parameters System

The parameters system handles configuration of all test aspects, including RDMA operations, connection types, test duration, message sizes, and more. It's implemented primarily in `perftest_parameters.c` with the central data structure `struct perftest_parameters`.

```mermaid
classDiagram
    class perftest_parameters {
        +connection_type
        +test_type
        +verb
        +size
        +iters
        +tx_depth
        +rx_depth
        +duration
        +memory_type
        +struct memory_ctx* (*memory_create)()
        +many more config fields...
    }
    
    note for perftest_parameters "Central configuration structure\nControls all test behavior"
```

Key aspects of the parameters system:
- Provides command-line argument parsing
- Sets default values for all test parameters
- Validates parameter combinations for compatibility
- Forces dependencies between related parameters

Sources:
- [src/perftest_parameters.c:817-966]() - `init_perftest_params` function initializes default values
- [src/perftest_parameters.c:1181-1403]() - `force_dependecies` function ensures parameter compatibility

### Resources Management

The resources management component handles creation, configuration, and destruction of all RDMA resources needed for testing. It's implemented in `perftest_resources.c` and organized around the `struct pingpong_context` structure.

```mermaid
classDiagram
    class pingpong_context {
        +struct ibv_context *context
        +struct ibv_pd *pd
        +struct ibv_mr **mr
        +struct ibv_cq *send_cq
        +struct ibv_cq *recv_cq
        +struct ibv_qp **qp
        +struct ibv_srq *srq
        +void **buf
        +struct memory_ctx *memory
        +many more fields...
    }
    
    note for pingpong_context "Core structure that holds all\nRDMA resources for testing"
```

Key aspects of the resources management:
- Allocating and deallocating RDMA resources (QPs, CQs, MRs)
- Device discovery and configuration
- Memory management for send/receive buffers
- Support for different QP types (RC, UC, UD, etc.)
- Handling special resources (XRC domains, address handles, etc.)

Sources:
- [src/perftest_resources.c:942-979]() - `ctx_find_dev` function discovers RDMA devices
- [src/perftest_resources.c:1030-1128]() - `alloc_ctx` function allocates context resources
- [src/perftest_resources.c:1132-1222]() - `dealloc_ctx` function deallocates context resources
- [src/perftest_resources.c:1228-1451]() - `destroy_ctx` function destroys RDMA resources

### Communication System

The communication system manages the connection establishment and data exchange between test nodes. It's implemented in `perftest_communication.c` and supports both socket-based (Ethernet) and RDMA-CM based connection methods.

```mermaid
classDiagram
    class perftest_comm {
        +struct pingpong_context *rdma_ctx
        +struct perftest_parameters *rdma_params
        +int sockfd
    }
    
    perftest_comm --> pingpong_context
    perftest_comm --> perftest_parameters
    
    note for perftest_comm "Handles communication between\ntest nodes for setup and coordination"
```

Key aspects of the communication system:
- Connection establishment (socket or RDMA CM)
- QP handshaking and address exchange
- Test parameter synchronization
- Version compatibility checking
- MTU negotiation

Sources:
- [src/perftest_communication.c:827-865]() - `set_up_connection` function prepares connection info
- [src/perftest_communication.c:958-1156]() - `rdma_client_connect` function implements RDMA CM client connection
- [src/perftest_communication.c:1189-1315]() - `rdma_server_connect` function implements RDMA CM server connection
- [src/perftest_communication.c:1455-1480]() - `establish_connection` function creates connection
- [src/perftest_communication.c:1487-1527]() - `ctx_hand_shake` function exchanges QP information

## Memory Subsystem

The memory subsystem provides an abstraction layer for different memory allocation mechanisms, supporting host memory, memory-mapped files, and various accelerator memories (CUDA, ROCm, etc.). This modular design allows tests to use different memory types without changing the test code.

```mermaid
graph TB
    subgraph "Memory Abstraction Layer"
        memory["memory_ctx interface"]
        memory --> |"Host Memory"| host_memory["host_memory.c"]
        memory --> |"Memory Mapped Files"| mmap_memory["mmap_memory.c"]
        
        subgraph "Accelerator Memory (optional)"
            memory -.-> |"CUDA API"| cuda_memory["cuda_memory.c"]
            memory -.-> |"ROCm API"| rocm_memory["rocm_memory.c"]
            memory -.-> |"Neuron API"| neuron_memory["neuron_memory.c"]
            memory -.-> |"Habana Labs API"| hl_memory["hl_memory.c"]
            memory -.-> |"MLU API"| mlu_memory["mlu_memory.c"]
        end
    end
    
    memory_ops["Memory Operations Interface"] --> memory
    
    subgraph "Optional Features"
        dma_buf["DMA-BUF Integration"]
        aes_xts["AES-XTS Encryption"]
        data_direct["Data Direct"]
        cuda_memory -.-> dma_buf
        rocm_memory -.-> dma_buf
        neuron_memory -.-> dma_buf
    end
    
    subgraph "Test Programs"
        tests["Test Programs"]
        tests --> memory_ops
    end
```

The memory subsystem utilizes a common interface defined by `struct memory_ctx` that all memory implementations must implement. This interface includes the following key operations:

- `init()`: Initialize the memory subsystem
- `destroy()`: Clean up the memory subsystem
- `allocate_buffer()`: Allocate memory of a specified size
- `free_buffer()`: Free previously allocated memory
- `copy_buffer_to_host()`: Copy from device/accelerator memory to host memory
- `copy_host_to_buffer()`: Copy from host memory to device/accelerator memory
- `copy_buffer_to_buffer()`: Copy between two device/accelerator memory locations

Sources:
- [src/perftest_resources.c:1108-1128]() - Memory allocation in context creation
- [src/perftest_parameters.c:886-896]() - Memory type initialization
- [src/perftest_communication.c:1368-1370]() - Memory context creation for communication

## Test Execution Flow

The following diagram illustrates the execution flow of a typical perftest run, from initialization through test execution to cleanup.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Network
    
    Note over Client,Server: Initialization Phase
    Client->>Client: Parse arguments
    Server->>Server: Parse arguments
    
    Client->>Client: Find RDMA device (ctx_find_dev)
    Server->>Server: Find RDMA device (ctx_find_dev)
    
    Client->>Client: Open device (ctx_open_device)
    Server->>Server: Open device (ctx_open_device)
    
    Client->>+Server: Establish connection (establish_connection)
    Server-->>-Client: Connection established
    
    Client->>Server: Exchange versions (exchange_versions)
    Client->>Server: Check system data (check_sys_data)
    Client->>Server: Check MTU (check_mtu)
    
    Note over Client,Server: Resource Setup Phase
    Client->>Client: Initialize context (ctx_init)
    Server->>Server: Initialize context (ctx_init)
    
    Client->>Client: Set up connection (set_up_connection)
    Server->>Server: Set up connection (set_up_connection)
    
    Client->>+Server: Exchange QP information (ctx_hand_shake)
    Server-->>-Client: QP information exchanged
    
    Client->>Client: Connect QPs (ctx_connect)
    Server->>Server: Connect QPs (ctx_connect)
    
    Note over Client,Server: Test Execution Phase
    alt Bandwidth Test
        Client->>Client: Warm up (perform_warm_up)
        Server->>Server: Post receive WQEs
        
        Client->>Network: Post send WQEs (run_iter_bw)
        Network->>Server: Receive data
        Server->>Network: Post ACKs
        Network->>Client: Receive ACKs
        
        Client->>Client: Calculate bandwidth
    else Latency Test
        loop For n iterations
            Client->>Network: Send packet
            Network->>Server: Receive packet
            Server->>Network: Send response
            Network->>Client: Receive response
            Client->>Client: Measure round-trip time
        end
        Client->>Client: Calculate statistics
    end
    
    Note over Client,Server: Cleanup Phase
    Client->>Server: Exchange reports (xchg_bw_reports)
    Client->>Client: Generate report
    
    Client->>Server: Close connection (ctx_close_connection)
    Client->>Client: Destroy context (destroy_ctx)
    Server->>Server: Destroy context (destroy_ctx)
```

Sources:
- [src/perftest_resources.c:897-921]() - `create_rdma_resources` function
- [src/perftest_resources.c:926-937]() - `destroy_rdma_resources` function
- [src/perftest_resources.c:1228-1451]() - `destroy_ctx` function for cleanup
- [src/perftest_communication.c:1455-1480]() - `establish_connection` function
- [src/perftest_communication.c:1487-1527]() - `ctx_hand_shake` function

## Test Types

Perftest includes three primary test types, each designed to measure different aspects of RDMA performance.

```mermaid
graph TD
    subgraph "Test Types"
        bw["Bandwidth Tests<br>ib_*_bw"]
        lat["Latency Tests<br>ib_*_lat"]
        fs["Flow Steering Rate Tests<br>raw_ethernet_fs_rate"]
    end
    
    subgraph "RDMA Verbs"
        send["SEND<br>ib_send_*"]
        write["WRITE<br>ib_write_*"]
        read["READ<br>ib_read_*"]
        atomic["ATOMIC<br>ib_atomic_*"]
    end
    
    bw --> send_bw["ib_send_bw"]
    bw --> write_bw["ib_write_bw"]
    bw --> read_bw["ib_read_bw"]
    bw --> atomic_bw["ib_atomic_bw"]
    bw --> raw_eth_bw["raw_ethernet_bw"]
    
    lat --> send_lat["ib_send_lat"]
    lat --> write_lat["ib_write_lat"]
    lat --> read_lat["ib_read_lat"]
    lat --> atomic_lat["ib_atomic_lat"]
    lat --> raw_eth_lat["raw_ethernet_lat"]
    lat --> raw_eth_burst["raw_ethernet_burst_lat"]

    fs --> raw_eth_fs["raw_ethernet_fs_rate"]
```

### Bandwidth Tests

Bandwidth tests measure the throughput of RDMA operations, expressed in terms of gigabits per second (Gbps) or bytes per second. These tests focus on maximum transfer rates achievable with different RDMA operations.

Key features of bandwidth tests:
- Support for all RDMA verbs (SEND, WRITE, READ, ATOMIC)
- Support for multiple outstanding operations (controlled by tx_depth)
- Bidirectional bandwidth measurement
- Post lists for efficient work request submission
- Support for various connection types (RC, UC, UD, etc.)

Sources:
- [src/perftest_parameters.c:849-850]() - Bandwidth test default settings
- [src/perftest_parameters.c:1359-1386]() - Post list configuration for bandwidth tests

### Latency Tests

Latency tests measure the round-trip time of RDMA operations, typically expressed in microseconds. These tests focus on the time it takes for a single operation to complete.

Key features of latency tests:
- Support for all RDMA verbs (SEND, WRITE, READ, ATOMIC)
- Histogram generation for detailed latency distribution analysis
- Cycle-based timing for high-precision measurement
- Support for various connection types (RC, UC, UD, etc.)

Sources:
- [src/perftest_parameters.c:312-315]() - Latency test command-line options
- [src/perftest_parameters.c:345-349]() - Latency histogram options

### Raw Ethernet Tests

Raw Ethernet tests operate at the Ethernet layer, bypassing the traditional IB/RDMA stack. These tests are useful for measuring raw network performance and special features like flow steering.

Key features of Raw Ethernet tests:
- Raw Ethernet bandwidth and latency measurements
- Flow steering rate testing
- Support for multi-flow traffic patterns
- MAC forwarding capabilities
- VLAN and QoS support

Sources:
- [src/perftest_parameters.c:725-813]() - Raw Ethernet command-line options
- [src/perftest_parameters.c:1145-1176]() - Flow rule dependencies

## Connection Types and Transport Modes

Perftest supports multiple connection types, allowing it to test various aspects of RDMA performance across different transport mechanisms.

```mermaid
graph LR
    subgraph "Connection Types"
        RC["RC<br>Reliable Connection"]
        UC["UC<br>Unreliable Connection"]
        UD["UD<br>Unreliable Datagram"]
        XRC["XRC<br>eXtended Reliable Connection"]
        DC["DC<br>Dynamically Connected"]
        SRD["SRD<br>Shared Receive Queue Datagram"]
        RawEth["Raw Ethernet"]
    end
    
    subgraph "Verbs Compatibility"
        SEND["SEND Verb"]
        WRITE["WRITE Verb"]
        READ["READ Verb"]
        ATOMIC["ATOMIC Verb"]
    end
    
    RC --> SEND & WRITE & READ & ATOMIC
    UC --> SEND & WRITE
    UD --> SEND
    XRC --> SEND & WRITE & READ & ATOMIC
    DC --> SEND & WRITE & READ & ATOMIC
    SRD --> SEND & WRITE & READ
    RawEth --> SEND
```

### Connection Types

- **RC (Reliable Connection)**: A connected transport providing reliable, in-order delivery with error checking. Supports all RDMA verbs.
- **UC (Unreliable Connection)**: A connected transport without guarantees of reliable delivery. Supports SEND and WRITE verbs.
- **UD (Unreliable Datagram)**: A connectionless transport allowing communication with multiple peers. Only supports SEND verb.
- **XRC (eXtended Reliable Connection)**: Similar to RC but with shared receive queues, optimized for many-to-one communication patterns.
- **DC (Dynamically Connected)**: Combines aspects of connected and connectionless transports, allowing dynamic connections to multiple peers.
- **SRD (Shared Receive Queue Datagram)**: Similar to UD but with shared receive queues.
- **Raw Ethernet**: Bypasses the RDMA stack entirely, operating directly at the Ethernet layer.

Sources:
- [src/perftest_parameters.c:1014-1061]() - Connection type selection and validation
- [src/perftest_parameters.c:1272-1285]() - XRC-specific configuration
- [src/perftest_parameters.c:1283-1285]() - DC-specific configuration

### RDMA Operations (Verbs)

- **SEND/RECV**: Requires coordination between sender and receiver, with explicit receive buffers posted by the receiver.
- **WRITE**: One-sided operation where the initiator writes data directly to a remote memory region.
- **READ**: One-sided operation where the initiator reads data directly from a remote memory region.
- **ATOMIC**: One-sided operation performing atomic operations (compare-and-swap, fetch-and-add) on remote memory.

The compatibility between verbs and connection types is enforced by validation checks in the parameters system.

Sources:
- [src/perftest_parameters.c:1014-1061]() - Validation of verb and connection type compatibility
- [src/perftest_parameters.c:1245-1246]() - READ and ATOMIC-specific handling

## Integration Points

Perftest includes several integration points with other systems and features:

1. **RDMA CM**: Support for RDMA Connection Manager for connection establishment instead of using sockets.
2. **Accelerator Memory**: Integration with GPU and other accelerator memory through the memory abstraction layer.
3. **DMA-BUF**: Support for sharing memory between devices using Linux DMA-BUF.
4. **Performance Counters**: Integration with IB performance counters for detailed performance analysis.
5. **Hardware Rate Limiting**: Support for QoS and rate limiting features of RDMA hardware.
6. **AES-XTS Encryption**: Support for hardware-accelerated encryption of RDMA traffic.

These integration points make perftest a comprehensive tool for testing RDMA performance in various environments and configurations.

Sources:
- [src/perftest_parameters.c:423-443]() - RDMA CM options
- [src/perftest_parameters.c:622-666]() - Accelerator memory options
- [src/perftest_communication.c:1381-1396]() - Performance counter setup

---

