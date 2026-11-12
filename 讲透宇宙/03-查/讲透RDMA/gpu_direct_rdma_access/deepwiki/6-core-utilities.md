<!-- source: DeepWiki mcp.deepwiki.com · repo Mellanox/gpu_direct_rdma_access · page 6 Core Utilities · fetched 2026-11-11 -->

# Core Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [utils.c](utils.c)
- [utils.h](utils.h)

</details>



## Purpose and Scope

The Core Utilities module provides essential support functions for network address resolution and performance measurement within the GPU Direct RDMA Access system. This module contains low-level utility functions that are used throughout the codebase for converting network addresses and measuring execution performance.

This page covers the utility functions defined in [utils.h]() and implemented in [utils.c](). For information about system configuration utilities and scripts, see [System Configuration Scripts](#7). For details about the main client and server applications that use these utilities, see [Client-Server Applications](#5).

## Utility Functions Overview

The core utilities module provides two primary categories of functionality through a simple C API:

| Function | Purpose | Input Parameters | Return Value |
|----------|---------|------------------|--------------|
| `get_addr` | Convert IP address string to `sockaddr` structure | hostname/IP string, sockaddr pointer | 0 on success, error code on failure |
| `print_run_time` | Calculate and display performance metrics | start time, data size, iteration count | 0 on success, 1 on error |

```mermaid
graph TB
    subgraph "Core Utilities Module"
        UTILS_H["utils.h<br/>Function Declarations"]
        UTILS_C["utils.c<br/>Function Implementations"]
        
        subgraph "Network Utilities"
            GET_ADDR["get_addr()<br/>Address Resolution"]
        end
        
        subgraph "Performance Utilities"
            PRINT_TIME["print_run_time()<br/>Performance Measurement"]
        end
    end
    
    subgraph "System Dependencies"
        LIBC["Standard C Library<br/>getaddrinfo, gettimeofday"]
        NETDB["Network Database<br/>Address Resolution"]
    end
    
    subgraph "Consuming Applications"
        CLIENT["client.c<br/>Client Application"]
        SERVER["server.c<br/>Server Application"]
    end
    
    UTILS_H --> GET_ADDR
    UTILS_H --> PRINT_TIME
    UTILS_C --> GET_ADDR
    UTILS_C --> PRINT_TIME
    
    GET_ADDR --> LIBC
    GET_ADDR --> NETDB
    PRINT_TIME --> LIBC
    
    CLIENT --> GET_ADDR
    CLIENT --> PRINT_TIME
    SERVER --> GET_ADDR
    SERVER --> PRINT_TIME
```

**Core Utilities Architecture**

Sources: [utils.h:1-61](), [utils.c:1-88]()

## Network Address Resolution

The `get_addr` function provides network address resolution capabilities by converting hostname strings or IP addresses into `sockaddr` structures suitable for network operations.

### Function Interface

The function signature is defined in [utils.h:45]():

```c
int get_addr(char *dst, struct sockaddr *addr);
```

### Implementation Details

The address resolution process follows this workflow:

```mermaid
flowchart TD
    START["get_addr() called"]
    GETADDRINFO["getaddrinfo(dst, NULL, NULL, &res)"]
    CHECK_ERROR{"getaddrinfo failed?"}
    ERROR_MSG["Print error message<br/>gai_strerror(ret)"]
    CHECK_FAMILY{"Address family?"}
    IPV4["PF_INET<br/>Copy sizeof(sockaddr_in)"]
    IPV6["PF_INET6<br/>Copy sizeof(sockaddr_in6)"]
    UNSUPPORTED["Set ret = -1<br/>Unsupported family"]
    CLEANUP["freeaddrinfo(res)"]
    RETURN["Return result code"]
    
    START --> GETADDRINFO
    GETADDRINFO --> CHECK_ERROR
    CHECK_ERROR -->|Yes| ERROR_MSG
    CHECK_ERROR -->|No| CHECK_FAMILY
    ERROR_MSG --> CLEANUP
    CHECK_FAMILY -->|PF_INET| IPV4
    CHECK_FAMILY -->|PF_INET6| IPV6
    CHECK_FAMILY -->|Other| UNSUPPORTED
    IPV4 --> CLEANUP
    IPV6 --> CLEANUP
    UNSUPPORTED --> CLEANUP
    CLEANUP --> RETURN
```

**Address Resolution Data Flow**

The implementation at [utils.c:44-64]() handles both IPv4 and IPv6 addresses:

- Uses `getaddrinfo()` for DNS resolution and address conversion
- Supports both hostname lookup and direct IP address conversion
- Copies the appropriate sockaddr structure based on address family
- Provides error handling with descriptive messages using `gai_strerror()`

Sources: [utils.c:44-64](), [utils.h:40-45]()

## Performance Measurement

The `print_run_time` function calculates and displays performance metrics for data transfer operations, providing both throughput and latency measurements.

### Function Interface

The function signature is defined in [utils.h:52]():

```c
int print_run_time(struct timeval start, unsigned long size, int iters);
```

### Measurement Calculations

The performance measurement process involves precise timing and throughput calculations:

```mermaid
graph TB
    subgraph "Performance Measurement Process"
        START_TIME["struct timeval start<br/>Initial timestamp"]
        END_TIME["gettimeofday(&end, NULL)<br/>Final timestamp"]
        
        subgraph "Time Calculation"
            USEC_CALC["usec = (end.tv_sec - start.tv_sec) * 1000000<br/>+ (end.tv_usec - start.tv_usec)"]
        end
        
        subgraph "Data Volume Calculation"
            BYTES_CALC["bytes = (long long) size * iters<br/>Total bytes transferred"]
        end
        
        subgraph "Performance Metrics"
            THROUGHPUT["Throughput: bytes * 8 / usec<br/>Megabits per second"]
            LATENCY["Latency: usec / iters<br/>Microseconds per iteration"]
        end
        
        subgraph "Output Display"
            THROUGHPUT_MSG["printf: X bytes in Y seconds = Z Mbit/sec"]
            LATENCY_MSG["printf: X iters in Y seconds = Z usec/iter"]
        end
    end
    
    START_TIME --> USEC_CALC
    END_TIME --> USEC_CALC
    USEC_CALC --> THROUGHPUT
    USEC_CALC --> LATENCY
    BYTES_CALC --> THROUGHPUT
    THROUGHPUT --> THROUGHPUT_MSG
    LATENCY --> LATENCY_MSG
```

**Performance Measurement Data Flow**

The implementation at [utils.c:66-86]() performs the following calculations:

- **Time Measurement**: Uses `gettimeofday()` to capture microsecond-precision timestamps
- **Throughput Calculation**: `(total_bytes * 8) / total_microseconds` for Mbit/sec
- **Latency Calculation**: `total_microseconds / iterations` for usec/iter
- **Data Volume**: `size * iterations` for total bytes processed

### Output Format

The function produces two lines of performance output:
1. Total data transferred with throughput in Mbit/sec
2. Total iterations with per-iteration latency in microseconds

Sources: [utils.c:66-86](), [utils.h:48-52]()

## Integration with System Components

The core utilities are used throughout the GPU Direct RDMA Access system:

```mermaid
graph LR
    subgraph "Core Utilities"
        GET_ADDR_FUNC["get_addr()"]
        PRINT_TIME_FUNC["print_run_time()"]
    end
    
    subgraph "Client Application"
        CLIENT_NET["Network Connection<br/>Setup"]
        CLIENT_PERF["Performance<br/>Measurement"]
    end
    
    subgraph "Server Application"
        SERVER_NET["Network Connection<br/>Handling"]
        SERVER_PERF["Benchmark<br/>Reporting"]
    end
    
    subgraph "RDMA Operations"
        RDMA_CONNECT["Connection<br/>Establishment"]
        RDMA_BENCH["Transfer<br/>Benchmarking"]
    end
    
    GET_ADDR_FUNC --> CLIENT_NET
    GET_ADDR_FUNC --> SERVER_NET
    CLIENT_NET --> RDMA_CONNECT
    SERVER_NET --> RDMA_CONNECT
    
    PRINT_TIME_FUNC --> CLIENT_PERF
    PRINT_TIME_FUNC --> SERVER_PERF
    CLIENT_PERF --> RDMA_BENCH
    SERVER_PERF --> RDMA_BENCH
```

**System Integration Overview**

The utilities provide essential infrastructure services:

- **Network Setup**: `get_addr()` enables hostname-to-address resolution for RDMA connections
- **Performance Analysis**: `print_run_time()` provides standardized benchmarking output across all applications
- **Cross-Platform Support**: Both functions handle IPv4/IPv6 and provide portable timing mechanisms

Sources: [utils.h:1-61](), [utils.c:1-88]()

---

