<!-- source: DeepWiki mcp.deepwiki.com · repo jonhoo/rust-ibverbs · page 7 Examples · fetched 2026-11-11 -->

# Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ibverbs/examples/devinfo.rs](ibverbs/examples/devinfo.rs)
- [ibverbs/examples/doorbell_batching.rs](ibverbs/examples/doorbell_batching.rs)
- [ibverbs/examples/efa_srd.rs](ibverbs/examples/efa_srd.rs)
- [ibverbs/examples/event_loop.rs](ibverbs/examples/event_loop.rs)
- [ibverbs/examples/loopback.rs](ibverbs/examples/loopback.rs)
- [ibverbs/examples/rdmacm_connect.rs](ibverbs/examples/rdmacm_connect.rs)

</details>



The `rust-ibverbs` repository includes a variety of runnable examples in the `ibverbs/examples/` directory. These examples serve as both functional tests and documentation for implementing RDMA patterns using the safe Rust API. They range from minimal loopback programs to complex connection management and hardware-specific features like AWS EFA.

### Running the Examples

Most examples target the first available RDMA device on the system. If physical RDMA hardware (InfiniBand, RoCE, or iWARP) is not available, you can use **SoftRoCE** (`rxe`) to run these examples over a standard Ethernet interface.

To create a SoftRoCE device:
```bash
# Replace <netdev> with your interface name, e.g., eth0 or enp0s3
sudo rdma link add rxe0 type rxe netdev <netdev>
```
Sources: [ibverbs/examples/loopback.rs:4-5](), [ibverbs/examples/doorbell_batching.rs:6-7]()

---

### Data-Path Patterns

These examples focus on the "Data-Path"—the high-performance movement of data using Send/Receive and RDMA Read/Write operations. They demonstrate different completion handling strategies and performance optimizations.

*   **`loopback.rs`**: The simplest complete program. It demonstrates a single `Rc` (Reliable Connected) Queue Pair connected to itself, performing a `post_recv` and a `send` before polling the `CompletionQueue`.
*   **`doorbell_batching.rs`**: Showcases performance optimization by chaining multiple work requests into a single "doorbell" ring using `QueuePair::start_send`. It demonstrates how to use unsignaled operations followed by a single signaled operation to minimize completion overhead.
*   **`event_loop.rs`**: Demonstrates event-driven completion handling. Instead of busy-polling, it uses a `CompletionChannel` to block on a file descriptor. It also shows how to multiplex multiple `CompletionQueue` objects onto a single channel using context cookies.

For detailed walkthroughs of these data-path implementations, see [Data-Path Examples (loopback, doorbell_batching, event_loop)](#7.1).

#### Data-Path Entity Mapping
The following diagram maps high-level RDMA concepts to the specific code entities used in these examples.

"Data-Path Entity Mapping"
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Memory Buffer"
        "Work Request"
        "Notification"
        "Batching"
    end

    subgraph "Code Entity Space"
        "MemoryRegion"["MemoryRegion [ibverbs/src/mr.rs]"]
        "RecvRequest"["RecvRequest [ibverbs/src/qp.rs]"]
        "SendBatch"["SendBatch [ibverbs/src/qp.rs]"]
        "CompChannel"["CompletionChannel [ibverbs/src/completion.rs]"]
        "WC"["WorkCompletion [ibverbs/src/completion.rs]"]
    end

    "Memory Buffer" --- "MemoryRegion"
    "Work Request" --- "RecvRequest"
    "Batching" --- "SendBatch"
    "Notification" --- "CompChannel"
    "Work Request" --- "WC"
```
Sources: [ibverbs/examples/loopback.rs:44-52](), [ibverbs/examples/doorbell_batching.rs:97-108](), [ibverbs/examples/event_loop.rs:52-64]()

---

### Connections and Device Discovery

These examples focus on the "Control-Path"—discovering hardware capabilities and establishing connections between different processes or specialized hardware.

*   **`rdmacm_connect.rs`**: Uses the RDMA Connection Manager (`rdmacm`) to establish a connection between a client and a server using IP addresses. This abstracts away the manual exchange of Queue Pair numbers and GIDs.
*   **`efa_srd.rs`**: A specialized example for AWS Elastic Fabric Adapter (EFA) hardware. It demonstrates the `Srd` (Scalable Reliable Datagram) transport type, which provides reliable delivery in a connectionless manner.
*   **`devinfo.rs`**: A diagnostic tool that enumerates all RDMA devices, queries their attributes (e.g., `max_qp`, `max_mr`), and prints port information similar to the standard `ibv_devinfo` utility.

For details on connection setup and hardware-specific APIs, see [Connection and Device Examples (rdmacm_connect, efa_srd, devinfo)](#7.2).

#### Connection Entity Mapping
This diagram bridges the gap between network connection concepts and the `rdmacm` abstraction layer.

"Connection Entity Mapping"
```mermaid
graph LR
    subgraph "Natural Language Space"
        "Server Listener"
        "Client Dialer"
        "Active Connection"
        "Device Discovery"
    end

    subgraph "Code Entity Space"
        "Acceptor"["Acceptor [ibverbs/src/rdmacm.rs]"]
        "Connector"["Connector [ibverbs/src/rdmacm.rs]"]
        "Conn"["Connection [ibverbs/src/rdmacm.rs]"]
        "DevList"["DeviceList [ibverbs/src/device.rs]"]
    end

    "Server Listener" --- "Acceptor"
    "Client Dialer" --- "Connector"
    "Active Connection" --- "Conn"
    "Device Discovery" --- "DevList"
```
Sources: [ibverbs/examples/rdmacm_connect.rs:54-92](), [ibverbs/examples/devinfo.rs:7-13]()

---

### Summary Table

| Example | Feature Highlight | Primary Types Used |
| :--- | :--- | :--- |
| `loopback` | Minimal RC Loopback | `Rc`, `QueuePair`, `CompletionQueue` |
| `doorbell_batching` | Chained WRs / Unsignaled Ops | `SendBatch`, `RemoteMemorySlice` |
| `event_loop` | Completion Channels / Epoll | `CompletionChannel`, `req_notify` |
| `rdmacm_connect` | IP-based Connection Setup | `Acceptor`, `Connector`, `Connection` |
| `efa_srd` | AWS EFA / SRD Transport | `Srd`, `AddressHandle` |
| `devinfo` | Hardware Query | `DeviceList`, `DeviceAttr`, `PortAttr` |

Sources: [ibverbs/examples/loopback.rs:1-78](), [ibverbs/examples/doorbell_batching.rs:1-158](), [ibverbs/examples/event_loop.rs:1-126](), [ibverbs/examples/rdmacm_connect.rs:1-117](), [ibverbs/examples/efa_srd.rs:1-79](), [ibverbs/examples/devinfo.rs:1-30]()

---

