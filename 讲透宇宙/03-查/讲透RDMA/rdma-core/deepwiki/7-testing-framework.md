<!-- source: DeepWiki mcp.deepwiki.com · repo linux-rdma/rdma-core · page 7 Testing Framework · fetched 2026-11-11 -->

# Testing Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Documentation/testing.md](Documentation/testing.md)
- [debian/python3-pyverbs.install](debian/python3-pyverbs.install)
- [tests/CMakeLists.txt](tests/CMakeLists.txt)
- [tests/__init__.py](tests/__init__.py)
- [tests/args_parser.py](tests/args_parser.py)
- [tests/base.py](tests/base.py)
- [tests/base_rdmacm.py](tests/base_rdmacm.py)
- [tests/cuda_utils.py](tests/cuda_utils.py)
- [tests/efa_base.py](tests/efa_base.py)
- [tests/irdma_base.py](tests/irdma_base.py)
- [tests/mlx5_base.py](tests/mlx5_base.py)
- [tests/mlx5_prm_structs.py](tests/mlx5_prm_structs.py)
- [tests/rdmacm_utils.py](tests/rdmacm_utils.py)
- [tests/run_tests.py](tests/run_tests.py)
- [tests/test_addr.py](tests/test_addr.py)
- [tests/test_atomic.py](tests/test_atomic.py)
- [tests/test_cq.py](tests/test_cq.py)
- [tests/test_cqex.py](tests/test_cqex.py)
- [tests/test_cuda_dmabuf.py](tests/test_cuda_dmabuf.py)
- [tests/test_device.py](tests/test_device.py)
- [tests/test_dmah.py](tests/test_dmah.py)
- [tests/test_efa_srd.py](tests/test_efa_srd.py)
- [tests/test_efadv.py](tests/test_efadv.py)
- [tests/test_flow.py](tests/test_flow.py)
- [tests/test_mlx5_cq.py](tests/test_mlx5_cq.py)
- [tests/test_mlx5_crypto.py](tests/test_mlx5_crypto.py)
- [tests/test_mlx5_cuda_umem.py](tests/test_mlx5_cuda_umem.py)
- [tests/test_mlx5_dc.py](tests/test_mlx5_dc.py)
- [tests/test_mlx5_devx.py](tests/test_mlx5_devx.py)
- [tests/test_mlx5_dr.py](tests/test_mlx5_dr.py)
- [tests/test_mlx5_flow.py](tests/test_mlx5_flow.py)
- [tests/test_mlx5_lag_affinity.py](tests/test_mlx5_lag_affinity.py)
- [tests/test_mlx5_mkey.py](tests/test_mlx5_mkey.py)
- [tests/test_mlx5_pp.py](tests/test_mlx5_pp.py)
- [tests/test_mlx5_rdma_ctrl.py](tests/test_mlx5_rdma_ctrl.py)
- [tests/test_mlx5_rdmacm.py](tests/test_mlx5_rdmacm.py)
- [tests/test_mlx5_sched.py](tests/test_mlx5_sched.py)
- [tests/test_mlx5_uar.py](tests/test_mlx5_uar.py)
- [tests/test_mlx5_udp_sport.py](tests/test_mlx5_udp_sport.py)
- [tests/test_mlx5_var.py](tests/test_mlx5_var.py)
- [tests/test_mlx5_vfio.py](tests/test_mlx5_vfio.py)
- [tests/test_mr.py](tests/test_mr.py)
- [tests/test_odp.py](tests/test_odp.py)
- [tests/test_parent_domain.py](tests/test_parent_domain.py)
- [tests/test_pd.py](tests/test_pd.py)
- [tests/test_qp.py](tests/test_qp.py)
- [tests/test_qpex.py](tests/test_qpex.py)
- [tests/test_rdmacm.py](tests/test_rdmacm.py)
- [tests/test_relaxed_ordering.py](tests/test_relaxed_ordering.py)
- [tests/test_rss_traffic.py](tests/test_rss_traffic.py)
- [tests/test_shared_pd.py](tests/test_shared_pd.py)
- [tests/utils.py](tests/utils.py)

</details>



## Purpose and Scope

This document describes the pytest-based testing infrastructure used to validate RDMA functionality in rdma-core. The test framework provides base classes for resource management, traffic generation utilities, and comprehensive test coverage for core verbs API, provider-specific extensions, and RDMA CM operations. For information about the Python bindings used by the tests, see [Core Pyverbs Bindings](#5.1). For provider-specific functionality, see [RDMA Providers](#3).

## Test Framework Architecture

The testing infrastructure is organized around a hierarchy of base classes that manage resource lifecycle and provide common testing patterns. Tests are implemented using the pytest framework and leverage pyverbs Python bindings to exercise the underlying C RDMA libraries.

### Base Test Classes

The framework provides three primary base test classes, each designed for different testing scenarios:

**Test Class Hierarchy**

```mermaid
graph TB
    unittest["unittest.TestCase"]
    
    subgraph "Base Test Classes"
        PyverbsAPITestCase["PyverbsAPITestCase"]
        RDMATestCase["RDMATestCase"]
        RDMACMBaseTest["RDMACMBaseTest"]
    end
    
    subgraph "Provider-Specific Base Classes"
        Mlx5PyverbsAPITestCase["Mlx5PyverbsAPITestCase"]
        Mlx5RDMATestCase["Mlx5RDMATestCase"]
        Mlx5RDMACMBaseTest["Mlx5RDMACMBaseTest"]
        EfaAPITestCase["EfaAPITestCase"]
        EfaRDMATestCase["EfaRDMATestCase"]
    end
    
    subgraph "Test Implementation Examples"
        DeviceTest["DeviceTest<br/>test_device.py"]
        QPTest["QPTest<br/>test_qp.py"]
        MRTest["MRTest<br/>test_mr.py"]
        OdpTestCase["OdpTestCase<br/>test_odp.py"]
        Mlx5DrTest["Mlx5DrTest<br/>test_mlx5_dr.py"]
        EfaQueryDeviceTest["EfaQueryDeviceTest<br/>test_efadv.py"]
    end
    
    unittest --> PyverbsAPITestCase
    unittest --> RDMATestCase
    RDMATestCase --> RDMACMBaseTest
    
    PyverbsAPITestCase --> Mlx5PyverbsAPITestCase
    RDMATestCase --> Mlx5RDMATestCase
    RDMACMBaseTest --> Mlx5RDMACMBaseTest
    PyverbsAPITestCase --> EfaAPITestCase
    RDMATestCase --> EfaRDMATestCase
    
    PyverbsAPITestCase --> DeviceTest
    PyverbsAPITestCase --> QPTest
    RDMATestCase --> MRTest
    RDMATestCase --> OdpTestCase
    Mlx5RDMATestCase --> Mlx5DrTest
    EfaAPITestCase --> EfaQueryDeviceTest
```

**PyverbsAPITestCase** ([tests/base.py:74-130]()) provides basic setup for testing device and context operations. It handles device selection from command-line arguments and performs device/port queries in `setUp()`.

**RDMATestCase** ([tests/base.py:132-373]()) extends PyverbsAPITestCase for traffic-oriented tests. It automatically discovers valid device/port/GID combinations, handles multiprocessing for two-node simulations, and provides the `create_players()` method to instantiate client and server resources.

**RDMACMBaseTest** ([tests/base.py:375-532]()) specializes RDMATestCase for RDMA CM testing. It adds IP address resolution and provides methods like `two_nodes_rdmacm_traffic()` for process-based connection testing with synchronization primitives.

Sources: [tests/base.py:74-532]()

### Resource Management Pattern

The framework uses resource aggregation classes that encapsulate all RDMA objects needed for testing. This pattern ensures proper resource cleanup and enables test parameterization.

**Resource Class Hierarchy**

```mermaid
graph TB
    BaseResources["BaseResources<br/>base.py"]
    TrafficResources["TrafficResources<br/>base.py"]
    RoCETrafficResources["RoCETrafficResources<br/>base.py"]
    
    subgraph "QP Type Resources"
        RCResources["RCResources<br/>RC QP"]
        UDResources["UDResources<br/>UD QP"]
        XRCResources["XRCResources<br/>XRC QP"]
        RawResources["RawResources<br/>Raw Packet QP"]
    end
    
    subgraph "Provider Resources"
        Mlx5DcResources["Mlx5DcResources<br/>mlx5_base.py<br/>DC QP"]
        Mlx5DevxRcResources["Mlx5DevxRcResources<br/>mlx5_base.py<br/>DevX RC"]
        SRDResources["SRDResources<br/>efa_base.py<br/>EFA SRD"]
    end
    
    subgraph "Feature Resources"
        OdpRC["OdpRC<br/>test_odp.py<br/>ODP MR"]
        Mlx5DrResources["Mlx5DrResources<br/>test_mlx5_dr.py<br/>Direct Rules"]
        MRRes["MRRes<br/>test_mr.py<br/>MR Testing"]
    end
    
    BaseResources --> TrafficResources
    TrafficResources --> RoCETrafficResources
    RoCETrafficResources --> RCResources
    RoCETrafficResources --> UDResources
    RoCETrafficResources --> XRCResources
    TrafficResources --> RawResources
    
    RoCETrafficResources --> Mlx5DcResources
    BaseResources --> Mlx5DevxRcResources
    TrafficResources --> SRDResources
    
    RCResources --> OdpRC
    RawResources --> Mlx5DrResources
    RCResources --> MRRes
```

The `SkipTestMeta` metaclass ([tests/base.py:550-559]()) automatically wraps `__init__` methods to catch `unittest.SkipTest` exceptions and ensure proper resource cleanup when a test needs to be skipped.

**Resource Lifecycle**

```mermaid
sequenceDiagram
    participant Test as "Test Method"
    participant Base as "RDMATestCase"
    participant Resource as "Resource Class"
    participant Cleanup as "tearDown()"
    
    Test->>Base: create_players(RCResources)
    Base->>Resource: __init__(dev_name, ib_port, gid_index)
    Resource->>Resource: create_context()
    Resource->>Resource: create_pd()
    Resource->>Resource: create_cq()
    Resource->>Resource: create_mr()
    Resource->>Resource: create_qps()
    Note over Resource: All resources created
    Resource->>Base: self.client, self.server
    Base->>Base: pre_run()
    Base->>Base: sync_remote_attr()
    Base-->>Test: Resources ready
    
    Test->>Test: Execute traffic
    Test->>Cleanup: Test complete
    Cleanup->>Resource: ctx.close()
    Note over Resource: All resources freed
```

Sources: [tests/base.py:562-729](), [tests/mlx5_base.py:122-207](), [tests/efa_base.py:48-114]()

## Test Utilities

The `tests/utils.py` module provides reusable helper functions for traffic generation, resource creation, and validation. These utilities abstract common patterns to reduce test code duplication.

### Traffic Pattern Functions

**Traffic Flow Components**

```mermaid
graph LR
    subgraph "Work Request Creation"
        get_send_elements["get_send_elements()<br/>utils.py:466-489"]
        get_recv_wr["get_recv_wr()<br/>utils.py:511-527"]
    end
    
    subgraph "Posting Operations"
        post_send["post_send()<br/>utils.py:619-638"]
        post_send_ex["post_send_ex()<br/>utils.py:563-617"]
        post_recv["post_recv()<br/>utils.py:641-656"]
    end
    
    subgraph "Completion Processing"
        poll_cq["poll_cq()<br/>utils.py:697-714"]
        poll_cq_ex["poll_cq_ex()<br/>utils.py:717-774"]
        validate["validate()<br/>utils.py:777-798"]
    end
    
    subgraph "Traffic Patterns"
        traffic["traffic()<br/>utils.py:855-933"]
        rdma_traffic["rdma_traffic()<br/>utils.py:936-988"]
        atomic_traffic["atomic_traffic()<br/>utils.py:991-1035"]
        xrc_traffic["xrc_traffic()<br/>utils.py:1038-1109"]
    end
    
    get_send_elements --> post_send
    get_send_elements --> post_send_ex
    get_recv_wr --> post_recv
    
    post_send --> poll_cq
    post_send_ex --> poll_cq_ex
    post_recv --> poll_cq
    
    poll_cq --> validate
    poll_cq_ex --> validate
    
    traffic --> get_send_elements
    traffic --> get_recv_wr
    traffic --> post_send
    traffic --> poll_cq
    
    rdma_traffic --> post_send_ex
    atomic_traffic --> post_send_ex
    xrc_traffic --> post_send
```

**Key Traffic Functions:**

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `traffic()` | Basic send/recv pingpong | client, server, iters, send_op |
| `rdma_traffic()` | RDMA write/read operations | Uses rkey/raddr for remote access |
| `atomic_traffic()` | Atomic compare-and-swap or fetch-and-add | receiver_val, sender_val |
| `xrc_traffic()` | XRC QP traffic with SRQ | Uses send and recv QP lists |
| `raw_traffic()` | Raw packet QP traffic | Ethernet frame construction |

Sources: [tests/utils.py:466-1109]()

### Resource Creation Helpers

**Helper Function Categories**

```mermaid
graph TB
    subgraph "MR Helpers"
        get_mr_length["get_mr_length()<br/>Random MR size"]
        get_access_flags["get_access_flags()<br/>Legal access combinations"]
        create_custom_mr["create_custom_mr()<br/>MR with specific flags"]
    end
    
    subgraph "QP Helpers"
        random_qp_cap["random_qp_cap()<br/>Valid QPCap"]
        random_qp_init_attr_ex["random_qp_init_attr_ex()<br/>QPInitAttrEx"]
        create_qp_ex["create_qp_ex()<br/>Extended QP"]
    end
    
    subgraph "DM Helpers"
        get_dm_attrs["get_dm_attrs()<br/>Device memory attrs"]
    end
    
    subgraph "AH Helpers"
        get_global_ah["get_global_ah()<br/>Address Handle"]
        get_global_route["get_global_route()<br/>Global Route"]
    end
    
    subgraph "Capability Checks"
        odp_supported["odp_supported()<br/>ODP capability"]
        requires_odp["@requires_odp<br/>Decorator"]
        requires_huge_pages["@requires_huge_pages<br/>Decorator"]
    end
```

The `get_access_flags()` function ([tests/utils.py:166-196]()) generates all legal combinations of MR access flags, filtering out invalid combinations like remote operations without local write ([tests/utils.py:154-163]()).

The `random_qp_init_attr_ex()` function ([tests/utils.py:334-369]()) creates valid `QPInitAttrEx` objects with randomized parameters constrained by device capabilities, useful for fuzz-style testing.

Sources: [tests/utils.py:143-382](), [tests/utils.py:530-552]()

### Packet Construction

For Raw Packet QP tests, the framework includes packet construction utilities:

```mermaid
graph TB
    subgraph "Packet Builders"
        gen_ethernet_header["gen_ethernet_header()"]
        gen_ipv4_header["gen_ipv4_header()"]
        gen_ipv6_header["gen_ipv6_header()"]
        gen_udp_header["gen_udp_header()"]
        gen_tcp_header["gen_tcp_header()"]
        gen_vxlan_header["gen_vxlan_header()"]
        gen_gre_header["gen_gre_header()"]
        gen_bth_header["gen_bth_header()"]
    end
    
    subgraph "Packet Parsing"
        RawPacket["RawPacket class"]
        parse_packet["parse_packet()"]
    end
    
    subgraph "Packet Constants"
        PacketConsts["PacketConsts<br/>SRC_MAC, DST_MAC<br/>SRC_IP, DST_IP<br/>Ports, VNI, etc."]
    end
    
    gen_ethernet_header --> RawPacket
    gen_ipv4_header --> RawPacket
    gen_udp_header --> RawPacket
    gen_vxlan_header --> RawPacket
    
    RawPacket --> parse_packet
    PacketConsts --> gen_ethernet_header
    PacketConsts --> gen_ipv4_header
```

The `PacketConsts` class ([tests/utils.py:68-122]()) provides standard values for constructing test packets with known headers.

Sources: [tests/utils.py:68-122](), [tests/utils.py:1112-1494]()

## Test Organization

Tests are organized by functionality and provider, enabling targeted test execution and clear separation of concerns.

### Test Categories

**Test Organization Structure**

```mermaid
graph TB
    subgraph "API Tests"
        test_device["test_device.py<br/>Context, query ops"]
        test_pd["test_pd.py<br/>PD operations"]
        test_mr["test_mr.py<br/>MR reg/dereg/rereg"]
        test_cq["test_cq.py<br/>CQ create/destroy"]
        test_qp["test_qp.py<br/>QP create/modify"]
        test_addr["test_addr.py<br/>AH operations"]
    end
    
    subgraph "Traffic Tests"
        test_qpex["test_qpex.py<br/>Extended post send"]
        test_odp["test_odp.py<br/>On-demand paging"]
        test_atomic["test_atomic.py<br/>Atomic operations"]
        test_flow["test_flow.py<br/>Flow steering"]
    end
    
    subgraph "MLX5 Tests"
        test_mlx5_dr["test_mlx5_dr.py<br/>Direct Rules"]
        test_mlx5_flow["test_mlx5_flow.py<br/>Flow matchers"]
        test_mlx5_dc["test_mlx5_dc.py<br/>DC QPs"]
        test_mlx5_devx["test_mlx5_devx.py<br/>DevX objects"]
    end
    
    subgraph "EFA Tests"
        test_efa_srd["test_efa_srd.py<br/>SRD transport"]
        test_efadv["test_efadv.py<br/>EFA direct verbs"]
    end
    
    subgraph "RDMA CM Tests"
        test_rdmacm["test_rdmacm.py<br/>Connection mgmt"]
        test_mlx5_rdmacm["test_mlx5_rdmacm.py<br/>MLX5 CM ext"]
    end
```

**API Tests** verify individual API operations without traffic. They use `PyverbsAPITestCase` ([tests/base.py:74]()) and focus on object creation, query, and modification operations.

**Traffic Tests** validate data plane operations. They use `RDMATestCase` ([tests/base.py:132]()) to set up two-node simulations and verify data integrity across send/recv or RDMA operations.

**Provider-Specific Tests** exercise vendor extensions and advanced features not available through standard verbs.

Sources: [tests/CMakeLists.txt:4-66]()

### Test Execution Model

**Pytest Execution Flow**

```mermaid
sequenceDiagram
    participant pytest as "pytest Runner"
    participant fixture as "Test Fixtures"
    participant test as "Test Method"
    participant base as "Base Class setUp()"
    participant traffic as "Traffic Utils"
    
    pytest->>fixture: Collect fixtures
    pytest->>test: Select test
    test->>base: setUp()
    base->>base: Parse args_parser config
    base->>base: Select dev/port/gid
    base->>base: Open context
    base-->>test: Environment ready
    
    test->>test: create_players()
    test->>test: Resource creation
    
    test->>traffic: traffic() or rdma_traffic()
    loop For each iteration
        traffic->>traffic: post_recv()
        traffic->>traffic: post_send()
        traffic->>traffic: poll_cq()
        traffic->>traffic: validate()
    end
    traffic-->>test: Traffic complete
    
    test->>base: tearDown()
    base->>base: Close resources
    base-->>pytest: Test complete
```

The framework uses `args_parser` ([tests/base.py:22]()) to handle command-line arguments:
- `--dev` - Device name
- `--port` - IB port number  
- `--gid` - GID index

Tests can be run selectively:
```bash
pytest tests/test_device.py  # Single file
pytest tests/test_device.py::DeviceTest::test_query_device  # Single test
pytest tests/ -k mlx5  # All MLX5 tests
```

Sources: [tests/base.py:74-108](), [tests/CMakeLists.txt:68-74]()

### RDMA CM Test Architecture

RDMA CM tests use multiprocessing to simulate active and passive connection sides:

**RDMA CM Test Flow**

```mermaid
graph TB
    subgraph "Main Process"
        test_method["test_rdmacm_sync_traffic()"]
        two_nodes["two_nodes_rdmacm_traffic()"]
    end
    
    subgraph "Passive Process"
        passive_init["CMSyncConnection<br/>passive=True"]
        passive_listen["rdma_listen()"]
        passive_accept["get_cm_event()<br/>RDMA_CM_EVENT_CONNECT_REQUEST"]
        passive_traffic["rdmacm_traffic()"]
    end
    
    subgraph "Active Process"
        active_init["CMSyncConnection<br/>passive=False"]
        active_resolve["rdma_resolve_addr()"]
        active_connect["rdma_connect()"]
        active_traffic["rdmacm_traffic()"]
    end
    
    subgraph "Synchronization"
        syncer["Barrier<br/>Process sync"]
        notifier["Queue<br/>Data exchange"]
    end
    
    test_method --> two_nodes
    two_nodes --> passive_init
    two_nodes --> active_init
    
    passive_init --> passive_listen
    passive_listen --> syncer
    
    active_init --> syncer
    syncer --> active_resolve
    active_resolve --> active_connect
    active_connect --> passive_accept
    
    passive_accept --> passive_traffic
    active_connect --> active_traffic
    
    passive_traffic --> notifier
    active_traffic --> notifier
```

The `CMConnection` abstract base class ([tests/rdmacm_utils.py:23-96]()) defines the connection interface, with implementations:
- `CMSyncConnection` ([tests/rdmacm_utils.py:133]()) - Uses synchronous `rdma_connect()`
- `CMAsyncConnection` ([tests/rdmacm_utils.py:231]()) - Uses asynchronous event handling

Sources: [tests/base.py:375-532](), [tests/rdmacm_utils.py:23-330]()

## Provider-Specific Testing

### MLX5 Testing Infrastructure

MLX5 tests leverage DevX for direct hardware access and advanced features:

**MLX5 Test Components**

```mermaid
graph TB
    subgraph "Base Classes"
        Mlx5PyverbsAPITestCase["Mlx5PyverbsAPITestCase<br/>mlx5_base.py:104-108"]
        Mlx5RDMATestCase["Mlx5RDMATestCase<br/>mlx5_base.py:110-114"]
    end
    
    subgraph "Resource Classes"
        Mlx5DcResources["Mlx5DcResources<br/>DC QP support<br/>mlx5_base.py:122-207"]
        Mlx5DevxRcResources["Mlx5DevxRcResources<br/>DevX RC QP<br/>mlx5_base.py:337-799"]
        Mlx5DrResources["Mlx5DrResources<br/>Direct Rules<br/>test_mlx5_dr.py:113-165"]
    end
    
    subgraph "PRM Structures"
        QueryHcaCapIn["QueryHcaCapIn<br/>mlx5_prm_structs.py"]
        CreateQpIn["CreateQpIn<br/>mlx5_prm_structs.py"]
        AllocFlowCounterIn["AllocFlowCounterIn<br/>mlx5_prm_structs.py"]
    end
    
    subgraph "Test Categories"
        test_mlx5_dr["test_mlx5_dr.py<br/>Flow steering"]
        test_mlx5_dc["test_mlx5_dc.py<br/>DC transport"]
        test_mlx5_devx["test_mlx5_devx.py<br/>DevX objects"]
        test_mlx5_flow["test_mlx5_flow.py<br/>Flow API"]
    end
    
    Mlx5PyverbsAPITestCase --> test_mlx5_devx
    Mlx5RDMATestCase --> test_mlx5_dr
    Mlx5RDMATestCase --> test_mlx5_dc
    
    Mlx5DcResources --> test_mlx5_dc
    Mlx5DevxRcResources --> test_mlx5_devx
    Mlx5DrResources --> test_mlx5_dr
    
    test_mlx5_devx --> PRM_Structures
    test_mlx5_dr --> PRM_Structures
```

The `mlx5_prm_structs.py` module ([tests/mlx5_prm_structs.py:1-1464]()) uses scapy to define PRM (Programmer's Reference Manual) structures as Python classes, enabling DevX command construction.

**Direct Rules Testing:**

MLX5 Direct Rules tests ([tests/test_mlx5_dr.py:190-1140]()) verify hardware steering capabilities:
- Domain creation via `DrDomain` ([tests/test_mlx5_dr.py:26]())
- Table and matcher setup via `DrTable` ([tests/test_mlx5_dr.py:27]()) and `DrMatcher` ([tests/test_mlx5_dr.py:25]())
- Rule insertion with various actions via `DrRule` ([tests/test_mlx5_dr.py:28]())
- Encap/decap packet reformat via `DrActionPacketReformat` ([tests/test_mlx5_dr.py:17]())

Sources: [tests/mlx5_base.py:104-289](), [tests/test_mlx5_dr.py:113-1140](), [tests/mlx5_prm_structs.py:1-1464]()

### EFA Testing Infrastructure

EFA tests focus on the SRD (Scalable Reliable Datagram) transport:

**EFA Test Structure**

```mermaid
graph TB
    subgraph "Base Classes"
        EfaAPITestCase["EfaAPITestCase<br/>efa_base.py:36-40"]
        EfaRDMATestCase["EfaRDMATestCase<br/>efa_base.py:42-46"]
    end
    
    subgraph "Resource Classes"
        SRDResources["SRDResources<br/>efa_base.py:48-114"]
        SRDQPConfig["SRD_QKEY: 0x11111111<br/>SRD_PKEY_INDEX: 0"]
    end
    
    subgraph "Test Categories"
        test_efadv["test_efadv.py<br/>Query device/AH"]
        test_efa_srd["test_efa_srd.py<br/>SRD traffic"]
    end
    
    EfaAPITestCase --> test_efadv
    EfaRDMATestCase --> test_efa_srd
    SRDResources --> test_efa_srd
    SRDResources --> SRDQPConfig
```

EFA tests use vendor-specific features:
- `EfaCQ` ([tests/utils.py:25]()) with scatter-gather read support
- `efadv` extensions for address resolution and device memory.

Sources: [tests/efa_base.py:1-114](), [tests/test_efa_srd.py:1-140](), [tests/test_efadv.py:1-166]()

## Running and Extending Tests

### Test Execution

Tests are installed via CMake ([tests/CMakeLists.txt:4-74]()) and can be run using pytest:

```bash
# Run all tests
pytest tests/

# Run with device specification
pytest tests/ --dev=mlx5_0 --port=1 --gid=3

# Run specific test categories
pytest tests/test_device.py tests/test_qp.py
```

The `run_tests.py` script ([tests/run_tests.py:69]()) provides a wrapper for test execution with additional filtering options.

### Skip Decorators

The framework provides decorators for conditional test skipping:

| Decorator | Purpose | Source |
|-----------|---------|--------|
| `@skip_unsupported` | Skip if operation returns EOPNOTSUPP | [tests/utils.py:1535-1548]() |
| `@requires_odp()` | Skip if ODP not supported for QP type | [tests/utils.py:1581-1598]() |
| `@requires_huge_pages()` | Skip if huge pages unavailable | [tests/utils.py:1600-1608]() |
| `@requires_root()` | Skip if not running as root | [tests/utils.py:1638-1644]() |
| `@requires_eth()` | Skip if not Ethernet link layer | [tests/utils.py:1646-1652]() |

Sources: [tests/utils.py:1535-1677]()

---

