<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/perftest · page 3 Bandwidth Tests · fetched 2026-11-11 -->

# Bandwidth Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/atomic_bw.c](src/atomic_bw.c)
- [src/read_bw.c](src/read_bw.c)
- [src/send_bw.c](src/send_bw.c)
- [src/write_bw.c](src/write_bw.c)

</details>



## Purpose and Overview

The bandwidth tests within the perftest suite measure the maximum throughput achievable over RDMA connections. These tests are essential for evaluating network performance, particularly for high-performance computing and datacenter applications where data transfer rates are critical.

This page documents the bandwidth test components in the perftest toolkit, covering their functionality, execution flow, and configuration options. For information about latency tests, see [Latency Tests](#4).

Sources: [src/write_bw.c:64-65](), [src/send_bw.c:177-178](), [src/read_bw.c:65-66](), [src/atomic_bw.c:65-66]()

## Available Bandwidth Tests

The perftest suite provides four bandwidth test programs, each measuring throughput for a different RDMA operation:

| Test Program | RDMA Operation | Description |
| ------------ | -------------- | ----------- |
| `ib_send_bw` | SEND | Measures bandwidth using SEND/RECV operations |
| `ib_write_bw` | WRITE | Measures bandwidth using RDMA WRITE operations |
| `ib_read_bw` | READ | Measures bandwidth using RDMA READ operations |
| `ib_atomic_bw` | ATOMIC | Measures bandwidth using atomic operations (CMP&SWP or FETCH&ADD) |

All bandwidth tests follow a similar structure and share core functionality, with each specializing in a particular RDMA operation.

Sources: [src/write_bw.c:64-65](), [src/send_bw.c:177-178](), [src/read_bw.c:65-66](), [src/atomic_bw.c:65-66]()

## Bandwidth Test Architecture

### Client-Server Model

Bandwidth tests operate using a client-server model where:

1. The server starts first and listens for incoming connections
2. The client initiates connection to the server
3. Both sides exchange setup parameters
4. The client initiates the test sequence
5. Both sides report results

This model allows for accurate measurement of one-way and bidirectional bandwidth.

#### Bandwidth Test Architecture Diagram

```mermaid
flowchart TB
    subgraph "Server Node"
        server_init["Initialize Parameters"]
        server_ctx["Create RDMA Context"]
        server_listen["Listen for Client"]
        server_handshake["Exchange Parameters"]
        server_setup["Set up QPs & Memory"]
        server_test["Run Test Loop"]
        server_report["Generate Report"]
        server_cleanup["Clean up Resources"]
        
        server_init --> server_ctx --> server_listen --> server_handshake --> server_setup --> server_test --> server_report --> server_cleanup
    end
    
    subgraph "Client Node"
        client_init["Initialize Parameters"]
        client_ctx["Create RDMA Context"]
        client_connect["Connect to Server"]
        client_handshake["Exchange Parameters"]
        client_setup["Set up QPs & Memory"]
        client_test["Run Test Loop"]
        client_report["Generate Report"]
        client_cleanup["Clean up Resources"]
        
        client_init --> client_ctx --> client_connect --> client_handshake --> client_setup --> client_test --> client_report --> client_cleanup
    end
    
    server_listen --- client_connect
    server_handshake --- client_handshake
    server_test --- client_test
    server_report --- client_report
```

Sources: [src/write_bw.c:114-122](), [src/send_bw.c:231-244](), [src/read_bw.c:109-121](), [src/atomic_bw.c:111-123]()

### Core Components

The bandwidth tests rely on several core components in the perftest suite:

```mermaid
classDiagram
    class perftest_parameters {
        +verb
        +tst
        +connection_type
        +test_method
        +tx_depth
        +rx_depth
        +iters
        +size
        +duplex
        +use_mcg
        +perform_warm_up
        +test_type
        +output
        +cpu_util_data
    }
    
    class pingpong_context {
        +struct ibv_context *context
        +struct ibv_pd *pd
        +struct ibv_mr **mr
        +struct ibv_cq *send_cq
        +struct ibv_cq *recv_cq
        +struct ibv_qp **qp
        +void **buf
    }
    
    class perftest_comm {
        +struct pingpong_context* rdma_ctx
        +struct perftest_parameters* rdma_params
        +int sockfd
    }
    
    class bw_report_data {
        +cycles_t start_time
        +cycles_t end_time
        +uint64_t bytes
        +int iters
        +double bw_peak
        +double bw_avg
        +double msg_rate_avg
        +double cpu_util
    }
    
    perftest_parameters --> pingpong_context : configures
    pingpong_context --> bw_report_data : generates
    perftest_comm --> pingpong_context : contains
    perftest_comm --> perftest_parameters : references
```

Sources: [src/write_bw.c:52-56](), [src/send_bw.c:159-165](), [src/read_bw.c:52-57](), [src/atomic_bw.c:51-57]()

## Test Execution Flow

### Test Initialization

The test initialization follows these steps:

1. Parse command-line arguments to configure test parameters
2. Find and open the specified InfiniBand device
3. Create communication structures for socket/RDMA CM connection
4. Establish connection between client and server
5. Exchange version information and system parameters
6. Allocate resources for the test (buffers, queue pairs, etc.)
7. Create RDMA resources (PD, MR, CQ, QP)
8. Set up the connection (post receive buffers, etc.)
9. Exchange connection parameters (QP numbers, etc.)
10. Move QPs to Ready-to-Send (RTS) state

Sources: [src/write_bw.c:69-97](), [src/send_bw.c:182-210](), [src/read_bw.c:69-101](), [src/atomic_bw.c:69-103]()

### Test Execution Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Note over Client,Server: Initialization Phase
    Client->>Client: Parse parameters
    Server->>Server: Parse parameters
    Client->>Client: Open IB device
    Server->>Server: Open IB device
    
    Client->>+Server: Establish connection
    Server-->>-Client: Connection ACK
    
    Client->>Server: Exchange versions
    Client->>Server: Exchange system data
    
    Note over Client,Server: Resource Setup Phase
    Client->>Client: ctx_init()
    Server->>Server: ctx_init()
    
    Client->>Client: set_up_connection()
    Server->>Server: set_up_connection()
    
    Client->>+Server: ctx_hand_shake()
    Server-->>-Client: Exchange QP information
    
    Client->>Client: ctx_connect()
    Server->>Server: ctx_connect()
    
    Note over Client,Server: Test Execution Phase
    
    alt Warm-up
        Client->>Client: perform_warm_up()
    end
    
    alt Run Regular Test
        Client->>Client: run_iter_bw()
        Server->>Server: Optional: run_iter_bw_server()
    else Run All Sizes
        loop For each message size
            Client->>Client: run_iter_bw()
            Server->>Server: Optional: run_iter_bw_server()
        end
    else Run Infinitely
        Client->>Client: run_iter_bw_infinitely()
        Server->>Server: Optional: run_iter_bw_infinitely_server()
    end
    
    Note over Client,Server: Results Phase
    Client->>Client: print_report_bw()
    
    alt Duplex Mode
        Client->>Server: xchg_bw_reports()
        Client->>Client: print_full_bw_report()
    end
    
    Note over Client,Server: Cleanup Phase
    Client->>+Server: ctx_close_connection()
    Server-->>-Client: Connection closed
    
    Client->>Client: destroy_ctx()
    Server->>Server: destroy_ctx()
```

Sources: [src/write_bw.c:296-476](), [src/send_bw.c:414-569](), [src/read_bw.c:302-395](), [src/atomic_bw.c:296-346]()

## Test Methods

The bandwidth tests support three test methods:

| Test Method | Description |
| ----------- | ----------- |
| `RUN_REGULAR` | Performs a single test with the specified message size |
| `RUN_ALL` | Runs tests with message sizes from 2^1 to 2^23 bytes |
| `RUN_INFINITELY` | Runs the test continuously until manually stopped |

Sources: [src/write_bw.c:302-447](), [src/send_bw.c:414-568](), [src/read_bw.c:302-394](), [src/atomic_bw.c:298-346]()

### Test Execution Process

The actual bandwidth measurement process follows these steps:

1. **Optional warm-up phase**: Performs initial operations to warm up the connection
2. **Test execution**: Performs the actual bandwidth measurement
   - For client: `run_iter_bw()` or `run_iter_bw_infinitely()`
   - For server (in some modes): `run_iter_bw_server()` or `run_iter_bw_infinitely_server()`
3. **Result calculation**: Calculates bandwidth based on the amount of data transferred and elapsed time
4. **Result reporting**: Generates and exchanges bandwidth reports

For duplex tests, both sides perform data transfers simultaneously.

Sources: [src/write_bw.c:319-357](), [src/send_bw.c:439-462](), [src/read_bw.c:346-365](), [src/atomic_bw.c:300-323]()

## Operation Types and Connection Modes

### RDMA Operations

Each bandwidth test focuses on a specific RDMA operation:

```mermaid
graph TD
    subgraph "RDMA Operation Types"
        send["SEND/RECV<br>(ib_send_bw)"]
        write["WRITE<br>(ib_write_bw)"]
        read["READ<br>(ib_read_bw)"]
        atomic["ATOMIC<br>(ib_atomic_bw)"]
    end
    
    subgraph "Transfer Direction"
        uni["Unidirectional<br>(default)"]
        bi["Duplex<br>(--bidirectional)"]
    end
    
    subgraph "Connection Types"
        rc["RC - Reliable Connection"]
        uc["UC - Unreliable Connection"]
        ud["UD - Unreliable Datagram"]
        xrc["XRC - eXtended Reliable Connection"]
        dc["DC - Dynamically Connected"]
    end
    
    send --> uni & bi
    write --> uni & bi
    read --> uni & bi
    atomic --> uni & bi
    
    uni & bi --> rc & uc & ud & xrc & dc
```

Sources: [src/write_bw.c:64](), [src/send_bw.c:177](), [src/read_bw.c:65](), [src/atomic_bw.c:65]()

### Connection Types

Bandwidth tests support multiple connection types with different characteristics:

| Connection Type | Description | Supported Operations |
| --------------- | ----------- | ------------------- |
| RC (Reliable Connection) | Provides reliable, connection-oriented transport | SEND, WRITE, READ, ATOMIC |
| UC (Unreliable Connection) | Connection-oriented but without reliability guarantees | SEND, WRITE |
| UD (Unreliable Datagram) | Connectionless, datagram-based transport | SEND only |
| XRC (eXtended Reliable Connection) | Allows sharing receive resources among connections | SEND, WRITE, READ, ATOMIC |
| DC (Dynamically Connected) | Provides dynamic connections to multiple destinations | SEND, WRITE, READ, ATOMIC |

Sources: [src/write_bw.c:76-78](), [src/send_bw.c:188-190](), [src/read_bw.c:76-78](), [src/atomic_bw.c:76-78]()

## Performance Measurement Details

### Bandwidth Calculation

Bandwidth is calculated using the following formula:

```
Bandwidth = (Total bytes transferred) / (Elapsed time)
```

The test reports multiple metrics:

1. **Bandwidth (MB/s or GB/s)**: Data transfer rate
2. **Message Rate (Msg/s)**: Number of messages per second
3. **CPU Utilization (%)**: Optional CPU usage measurement during the test

Sources: [src/write_bw.c:365-366](), [src/send_bw.c:464-516](), [src/read_bw.c:335-365](), [src/atomic_bw.c:319]()

### Result Reporting

Results are reported in a structured format:

```
------------------------------------------------------------------
                    RDMA_Write BW Test
 Dual-port       : OFF		Device         : mlx5_0
 Number of qps   : 1		Transport type : IB
 Connection type : RC		Using SRQ      : OFF
 TX depth        : 128
 CQ Moderation   : 100
 Mtu             : 4096[B]
 Link type       : IB
 GID index       : 3
 Max inline data : 0[B]
 rdma_cm QPs	 : OFF
 Data ex. method : Ethernet
------------------------------------------------------------------
 local address: LID 0x00 QPN 0x0137 PSN 0x3b5c1d RKey 0x00370f VAddr 0x007fe8286ed000
 remote address: LID 0x00 QPN 0x0136 PSN 0x475031 RKey 0x002c23 VAddr 0x007f146e7a5000
------------------------------------------------------------------
 #bytes     #iterations    BW peak[MB/s]    BW average[MB/s]   MsgRate[Mpps]
 65536      5000           6481.10          6477.45            0.103639      
------------------------------------------------------------------
```

For duplex tests, results from both sides are reported.

Sources: [src/write_bw.c:231-242](), [src/send_bw.c:402-412](), [src/read_bw.c:226-236](), [src/atomic_bw.c:291-294]()

## Special Considerations

### Warm-Up Phase

Bandwidth tests can include an optional warm-up phase to eliminate initialization effects from measurements. This helps obtain more accurate and consistent results.

Sources: [src/write_bw.c:319-328](), [src/send_bw.c:387-393](), [src/read_bw.c:346-351](), [src/atomic_bw.c:300-304]()

### Multicast Support

The `ib_send_bw` test supports multicast operations (`--use_mcg`) for testing group communication performance.

Sources: [src/send_bw.c:99-120]()

### RDMA CM Support

All bandwidth tests can use RDMA Connection Manager (RDMA CM) instead of the traditional IB verbs connection setup, which is useful for environments like RoCE.

Sources: [src/write_bw.c:150-166](), [src/send_bw.c:272-288](), [src/read_bw.c:145-161](), [src/atomic_bw.c:146-162]()

## Relationship to Other Components

Bandwidth tests utilize several core components from the perftest suite:

```mermaid
graph TD
    subgraph "Bandwidth Tests"
        ib_write_bw["ib_write_bw"]
        ib_send_bw["ib_send_bw"]
        ib_read_bw["ib_read_bw"]
        ib_atomic_bw["ib_atomic_bw"]
    end
    
    subgraph "Core Library"
        resources["perftest_resources.c"]
        parameters["perftest_parameters.c"]
        communication["perftest_communication.c"]
        clock["get_clock.c"]
    end
    
    subgraph "Memory Subsystem"
        memory["Memory Interface"]
    end
    
    ib_write_bw & ib_send_bw & ib_read_bw & ib_atomic_bw --> resources
    ib_write_bw & ib_send_bw & ib_read_bw & ib_atomic_bw --> parameters
    ib_write_bw & ib_send_bw & ib_read_bw & ib_atomic_bw --> communication
    resources --> memory
    resources --> clock
    parameters --> resources
```

Sources: [src/write_bw.c:41-44](), [src/send_bw.c:41-44](), [src/read_bw.c:41-43](), [src/atomic_bw.c:41-43]()

## Summary

Bandwidth tests in the perftest suite provide a comprehensive way to measure RDMA performance across different operation types and connection modes. They offer flexible configuration options and detailed performance metrics to help users evaluate and optimize their RDMA networks.

For specific test options and usage examples, refer to the [Command Line Interface](#7) page.

---

