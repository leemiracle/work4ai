<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/gpu_direct_rdma_access · page 5 Client-Server Applications · fetched 2026-11-11 -->

# Client-Server Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [client.c](client.c)
- [server.c](server.c)

</details>



This document covers the main application programs that demonstrate GPU Direct RDMA capabilities using Dynamic Connect Queue Pairs. The client and server applications work together to perform high-performance memory transfers between distributed systems, with the client capable of using either GPU or CPU memory while the server performs RDMA operations directly to the client's allocated buffers.

For details about the underlying RDMA engine used by these applications, see [Core RDMA Engine](#3). For information about memory allocation strategies, see [Memory Management Subsystem](#4).

## Application Architecture

The system implements a client-server architecture where the client allocates memory buffers and the server performs RDMA operations to those buffers. The applications use a hybrid communication model with TCP for control messages and RDMA for high-performance data transfer.

```mermaid
graph TB
    subgraph "Client Machine"
        CLIENT["client.c<br/>main()"]
        CLIENT_MEM["Memory Buffer<br/>CPU or GPU"]
        CLIENT_RDMA["RDMA Registration<br/>rdma_buffer_reg()"]
        CLIENT_TCP["TCP Socket<br/>open_client_socket()"]
    end
    
    subgraph "Server Machine"
        SERVER["server.c<br/>main()"]
        SERVER_MEM["CPU Memory Buffer<br/>work_buffer_alloc()"]
        SERVER_RDMA["RDMA Operations<br/>rdma_submit_task()"]
        SERVER_TCP["TCP Socket<br/>open_server_socket()"]
    end
    
    subgraph "Communication Channels"
        TCP_CTRL["TCP Control Channel<br/>Buffer Metadata & ACK"]
        RDMA_DATA["RDMA Data Channel<br/>Direct Memory Access"]
    end
    
    CLIENT --> CLIENT_MEM
    CLIENT_MEM --> CLIENT_RDMA
    CLIENT --> CLIENT_TCP
    CLIENT_TCP --> TCP_CTRL
    
    SERVER --> SERVER_MEM
    SERVER --> SERVER_TCP
    SERVER_TCP --> TCP_CTRL
    SERVER --> SERVER_RDMA
    SERVER_RDMA --> RDMA_DATA
    
    TCP_CTRL --> SERVER_TCP
    RDMA_DATA --> CLIENT_MEM
```

Sources: [client.c:302-466](), [server.c:239-427](), [README.md:1-91]()

## Communication Protocol

The applications implement a multi-phase protocol that separates control operations (over TCP) from data operations (over RDMA). Each iteration follows a strict sequence to ensure synchronization between client and server.

```mermaid
sequenceDiagram
    participant C as "Client<br/>client.c"
    participant TCP as "TCP Channel"
    participant S as "Server<br/>server.c"
    participant RDMA as "RDMA Channel"
    
    C->>C: "work_buffer_alloc()"
    C->>C: "rdma_buffer_reg()"
    C->>TCP: "connect(servername, port)"
    TCP->>S: "accept() connection"
    
    loop "for each iteration"
        C->>C: "pack_payload_data(RDMA_BUF_DESC)"
        C->>C: "pack_payload_data(TASK_ATTRS)"
        C->>TCP: "write(buffer_desc + task_attrs)"
        TCP->>S: "recv(buffer_desc + task_attrs)"
        S->>S: "rdma_submit_task()"
        S->>RDMA: "RDMA Write/Read to client buffer"
        RDMA->>C: "Direct memory access"
        S->>S: "rdma_poll_completions()"
        S->>TCP: "write(ACK_MSG)"
        TCP->>C: "recv(ACK_MSG)"
    end
```

Sources: [client.c:410-437](), [server.c:300-404](), [client.c:144-159]()

## Application Lifecycle

Both applications follow structured initialization, execution, and cleanup phases. The server can operate in persistent mode to handle multiple client connections sequentially.

### Client Application Lifecycle

```mermaid
graph TD
    START["main()"] --> PARSE["parse_command_line()"]
    PARSE --> VALIDATE["Validate hostaddr"]
    VALIDATE --> SOCKET["open_client_socket()"]
    SOCKET --> RDMA_DEV["rdma_open_device_client()"]
    RDMA_DEV --> MEM_ALLOC["work_buffer_alloc()<br/>CPU or GPU"]
    MEM_ALLOC --> RDMA_REG["rdma_buffer_reg()"]
    RDMA_REG --> DESC_STR["rdma_buffer_get_desc_str()"]
    DESC_STR --> TASK_STR["rdma_task_attr_flags_get_desc_str()"]
    TASK_STR --> PACKAGE["pack_payload_data()"]
    PACKAGE --> LOOP["Iteration Loop<br/>send/recv cycles"]
    LOOP --> TIMING["print_run_time()"]
    TIMING --> CLEANUP["Cleanup Resources"]
    
    CLEANUP --> CLEAN_PKG["free(package)"]
    CLEAN_PKG --> CLEAN_RDMA["rdma_buffer_dereg()"]
    CLEAN_RDMA --> CLEAN_MEM["work_buffer_free()"]
    CLEAN_MEM --> CLEAN_DEV["rdma_close_device()"]
    CLEAN_DEV --> CLEAN_SOCK["close(sockfd)"]
    CLEAN_SOCK --> END["return ret_val"]
```

Sources: [client.c:302-466](), [client.c:206-300]()

### Server Application Lifecycle

```mermaid
graph TD
    START["main()"] --> PARSE["parse_command_line()"]
    PARSE --> RDMA_DEV["rdma_open_device_server()"]
    RDMA_DEV --> MEM_ALLOC["work_buffer_alloc()<br/>CPU only"]
    MEM_ALLOC --> RDMA_REG["rdma_buffer_reg()"]
    RDMA_REG --> SIGNAL["Setup sigint_handler()"]
    SIGNAL --> LISTEN["open_server_socket()"]
    LISTEN --> TIMING["gettimeofday(&start)"]
    TIMING --> LOOP["Iteration Loop"]
    
    LOOP --> RECV_DESC["recv(RDMA_BUF_DESC)"]
    RECV_DESC --> RECV_TASK["recv(TASK_ATTRS)"]
    RECV_TASK --> SUBMIT["rdma_submit_task()"]
    SUBMIT --> POLL["rdma_poll_completions()"]
    POLL --> ACK["write(ACK_MSG)"]
    ACK --> CHECK{"keep_running &&<br/>cnt < iters?"}
    CHECK -->|Yes| LOOP
    CHECK -->|No| PRINT_TIME["print_run_time()"]
    
    PRINT_TIME --> CLOSE_SOCK["close(sockfd)"]
    CLOSE_SOCK --> PERSISTENT{"persistent &&<br/>keep_running?"}
    PERSISTENT -->|Yes| LISTEN
    PERSISTENT -->|No| CLEANUP["Cleanup Resources"]
    
    CLEANUP --> CLEAN_RDMA["rdma_buffer_dereg()"]
    CLEAN_RDMA --> CLEAN_MEM["work_buffer_free()"]
    CLEAN_MEM --> CLEAN_DEV["rdma_close_device()"]
    CLEAN_DEV --> END["return ret_val"]
```

Sources: [server.c:239-427](), [server.c:162-237](), [server.c:283-415]()

## Command Line Interfaces

Both applications provide comprehensive command line interfaces for configuration. The client supports GPU device selection while the server focuses on network and performance parameters.

### Client Parameters

| Parameter | Description | Default | Code Reference |
|-----------|-------------|---------|----------------|
| `-t, --task-flags` | RDMA operation type (0=WRITE, 1=READ) | 0 | [client.c:236-238]() |
| `-a, --addr` | Local host IP address (mandatory) | None | [client.c:240-242]() |
| `-p, --port` | Server port number | 18515 | [client.c:244-250]() |
| `-s, --size` | Message size in bytes | 4096 | [client.c:252-254]() |
| `-n, --iters` | Number of iterations | 1000 | [client.c:256-258]() |
| `-u, --use-cuda` | GPU device BDF (e.g., "3e:02.0") | None | [client.c:260-268]() |
| `-D, --debug-mask` | Debug flags (bit 0=debug, bit 1=fast path) | 0 | [client.c:270-273]() |

### Server Parameters

| Parameter | Description | Default | Code Reference |
|-----------|-------------|---------|----------------|
| `-P, --persistent` | Handle multiple client connections | 0 | [server.c:192-194]() |
| `-a, --addr` | Local host IP address (mandatory) | None | [server.c:196-198]() |
| `-p, --port` | Listen port number | 18515 | [server.c:200-206]() |
| `-s, --size` | Message size in bytes | 4096 | [server.c:208-210]() |
| `-n, --iters` | Number of iterations | 1000 | [server.c:212-214]() |
| `-l, --sg_list-len` | Scatter-gather list length | 0 | [server.c:216-218]() |
| `-D, --debug-mask` | Debug flags (bit 0=debug, bit 1=fast path) | 0 | [server.c:220-223]() |

Sources: [client.c:188-204](), [server.c:146-160](), [client.c:206-300](), [server.c:162-237]()

## Data Packaging Protocol

The client implements a custom protocol for sending buffer metadata and task attributes to the server. This protocol uses type-length-value encoding to support extensible message formats.

```mermaid
graph LR
    subgraph "Package Structure"
        TYPE1["uint8_t<br/>payload_t<br/>(RDMA_BUF_DESC)"]
        SIZE1["uint16_t<br/>payload_size"]
        DATA1["char*<br/>buffer_desc_str"]
        TYPE2["uint8_t<br/>payload_t<br/>(TASK_ATTRS)"]
        SIZE2["uint16_t<br/>payload_size"]
        DATA2["char*<br/>task_flags_str"]
    end
    
    TYPE1 --> SIZE1
    SIZE1 --> DATA1
    DATA1 --> TYPE2
    TYPE2 --> SIZE2
    SIZE2 --> DATA2
```

The `pack_payload_data()` function [client.c:144-159]() implements this protocol, while the server parses packages using the `recv()` loop [server.c:313-340]().

Sources: [client.c:123-159](), [client.c:378-398](), [server.c:313-340]()

## Memory Allocation Strategies

The applications use different memory allocation strategies based on their roles and hardware capabilities:

### Client Memory Allocation

```mermaid
graph TD
    CLIENT_ALLOC["work_buffer_alloc()"] --> CUDA_CHECK{"usr_par.use_cuda?"}
    CUDA_CHECK -->|Yes| GPU_ALLOC["GPU Memory<br/>CUDA allocation<br/>with BDF selection"]
    CUDA_CHECK -->|No| CPU_ALLOC["CPU Memory<br/>memalign() allocation"]
    
    GPU_ALLOC --> RDMA_REG["rdma_buffer_reg()"]
    CPU_ALLOC --> RDMA_REG
    RDMA_REG --> DESC_GEN["rdma_buffer_get_desc_str()"]
```

### Server Memory Allocation

```mermaid
graph TD
    SERVER_ALLOC["work_buffer_alloc()"] --> CPU_ONLY["CPU Memory Only<br/>use_cuda = 0"]
    CPU_ONLY --> RDMA_REG["rdma_buffer_reg()"]
    RDMA_REG --> TASK_SUBMIT["rdma_submit_task()"]
```

The client memory allocation [client.c:346-351]() supports both CPU and GPU memory based on the `use_cuda` parameter and optional BDF specification, while the server [server.c:264-268]() always uses CPU memory for its local buffer.

Sources: [client.c:346-357](), [server.c:264-268](), [client.c:260-268]()

## Error Handling and Recovery

Both applications implement comprehensive error handling with proper resource cleanup. The server supports device reset for error recovery in persistent mode.

### Error Handling Flow

```mermaid
graph TD
    ERROR["Error Detected"] --> CHECK_PERSISTENT{"persistent &&<br/>keep_running?"}
    CHECK_PERSISTENT -->|Yes| RESET["rdma_reset_device()"]
    CHECK_PERSISTENT -->|No| CLEANUP["Standard Cleanup"]
    
    RESET --> CONTINUE["Continue Operation"]
    CLEANUP --> EXIT["Application Exit"]
    
    subgraph "Cleanup Sequence"
        CLEAN_SOCK["close(sockfd)"]
        CLEAN_RDMA["rdma_buffer_dereg()"]
        CLEAN_MEM["work_buffer_free()"]
        CLEAN_DEV["rdma_close_device()"]
        
        CLEAN_SOCK --> CLEAN_RDMA
        CLEAN_RDMA --> CLEAN_MEM
        CLEAN_MEM --> CLEAN_DEV
    end
```

The server implements RDMA device reset [server.c:392-393]() for error recovery, while both applications use labeled goto statements for structured cleanup [client.c:445-464](), [server.c:412-426]().

Sources: [server.c:385-396](), [client.c:445-464](), [server.c:412-426]()

---

