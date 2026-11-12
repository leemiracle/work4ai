<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuopt · extra page gRPC Clients (C++, Python, Routing) · fetched 2026-10-26 -->

# gRPC Clients (C++, Python, Routing)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpp/cuopt_cli.cpp](cpp/cuopt_cli.cpp)
- [cpp/include/cuopt/grpc/cython_grpc_client.hpp](cpp/include/cuopt/grpc/cython_grpc_client.hpp)
- [cpp/include/cuopt/mathematical_optimization/solve_remote.hpp](cpp/include/cuopt/mathematical_optimization/solve_remote.hpp)
- [cpp/src/grpc/client/cython_grpc_client.cpp](cpp/src/grpc/client/cython_grpc_client.cpp)
- [cpp/src/grpc/client/grpc_client.cpp](cpp/src/grpc/client/grpc_client.cpp)
- [cpp/src/grpc/client/grpc_client.hpp](cpp/src/grpc/client/grpc_client.hpp)
- [cpp/src/grpc/client/solve_remote.cpp](cpp/src/grpc/client/solve_remote.cpp)
- [cpp/src/grpc/cuopt_remote_service.proto](cpp/src/grpc/cuopt_remote_service.proto)
- [cpp/src/grpc/grpc_service_mapper.cpp](cpp/src/grpc/grpc_service_mapper.cpp)
- [cpp/src/grpc/grpc_service_mapper.hpp](cpp/src/grpc/grpc_service_mapper.hpp)
- [cpp/src/grpc/grpc_settings_mapper.cpp](cpp/src/grpc/grpc_settings_mapper.cpp)
- [cpp/src/grpc/grpc_settings_mapper.hpp](cpp/src/grpc/grpc_settings_mapper.hpp)
- [cpp/tests/linear_programming/grpc/grpc_client_test.cpp](cpp/tests/linear_programming/grpc/grpc_client_test.cpp)
- [docs/cuopt/source/cuopt-grpc/examples/remote_routing_demo.py](docs/cuopt/source/cuopt-grpc/examples/remote_routing_demo.py)
- [docs/cuopt/source/cuopt-grpc/routing.rst](docs/cuopt/source/cuopt-grpc/routing.rst)
- [python/cuopt/cuopt/grpc/client/grpc_client.pxd](python/cuopt/cuopt/grpc/client/grpc_client.pxd)
- [python/cuopt/cuopt/grpc/client/grpc_client.pyx](python/cuopt/cuopt/grpc/client/grpc_client.pyx)
- [python/cuopt/cuopt/grpc/routing/__init__.py](python/cuopt/cuopt/grpc/routing/__init__.py)
- [python/cuopt/cuopt/grpc/routing/grpc_client.py](python/cuopt/cuopt/grpc/routing/grpc_client.py)
- [python/cuopt/cuopt/tests/routing/test_routing_grpc_client.py](python/cuopt/cuopt/tests/routing/test_routing_grpc_client.py)
- [python/cuopt/cuopt/tests/routing/test_routing_grpc_client_tls.py](python/cuopt/cuopt/tests/routing/test_routing_grpc_client_tls.py)
- [python/cuopt_server/cuopt_server/proxy_webserver.py](python/cuopt_server/cuopt_server/proxy_webserver.py)
- [python/cuopt_server/cuopt_server/tests/test_grpc_http_proxy.py](python/cuopt_server/cuopt_server/tests/test_grpc_http_proxy.py)

</details>



## Purpose and Scope
This page details the remote gRPC execution architecture in cuOpt, focusing on the C++ `grpc_client_t` client interface, remote solve wrappers (`solve_lp_remote`/`solve_mip_remote`), the Cython-to-C++ bridge (`grpc_python_client_t`), the routing gRPC client integration, transport layer security (TLS/mTLS) configurations, and the FastAPI-based HTTP proxy webserver bridge (`cuopt_server`).

---

## 1. C++ `grpc_client_t` Architecture and Implementation

The C++ client core is encapsulated by `grpc_client_t`, which communicates with the cuOpt gRPC remote service using a PIMPL design pattern (`impl_t`) to isolate gRPC dependency headers from public APIs.

Configuration parameters are specified via `grpc_client_config_t` [cpp/src/grpc/client/grpc_client.hpp:61-107](), which governs timeout behaviors, message sizing floors/ceilings, chunking thresholds, and TLS options.

```mermaid
graph TD
    subgraph Natural Language Space
        A[""User C++ Code""] --> B[""gRPC Client Configuration""]
        B --> C[""Chunked / Unary RPC Submission""]
    end
    subgraph Code Entity Space
        D[""cuopt::mathematical_optimization::grpc_client_t"""] --> E[""grpc_client_config_t"""]
        E --> F[""impl_t PIMPL Struct"""]
        F --> G[""cuopt::remote::CuOptRemoteService::StubInterface"""]
    end
    A -.-> D
    B -.-> E
    C -.-> G
```
*Diagram: Bridging user-facing gRPC client configuration to `grpc_client_t` and `StubInterface`.*

Sources: `[cpp/src/grpc/client/grpc_client.hpp:61-107]()`, `[cpp/src/grpc/client/grpc_client.cpp:78-85]()`

---

## 2. Remote Solve Helpers (`solve_lp_remote`, `solve_mip_remote`)

Remote invocation helpers (`solve_lp_remote` and `solve_mip_remote`) handle translation of local optimization problems into gRPC requests, dispatching jobs, polling for completion status, and fetching final solutions or streaming intermediate incumbents.

- **Unary vs. Chunked Transfers**: For payloads smaller than `max_message_bytes`, the client uses unary `SubmitJob` calls. For payloads exceeding the threshold, it switches to the chunked array protocol (`StartChunkedUpload`, multiple `SendArrayChunk` calls, and `FinishChunkedUpload`) [cpp/src/grpc/client/grpc_client.hpp:61]().
- **Incumbent Streaming**: MIP solves can register an incumbent callback via `grpc_client_config_t::incumbent_callback` to receive better-feasible solutions incrementally [cpp/src/grpc/client/grpc_client.hpp:68-74]().

Sources: `[cpp/src/grpc/client/grpc_client.hpp:61-90]()`, `[cpp/tests/linear_programming/grpc/grpc_client_test.cpp:57-107]()`

---

## 3. Cython Bridge (`grpc_python_client_t`) and Type Conversion

Python bindings interact with the C++ gRPC core via the owning wrapper `grpc_python_client_t`, defined in C++ [cpp/include/cuopt/grpc/cython_grpc_client.hpp:121-202]() and exposed through Cython in `grpc_client.pyx` [python/cuopt/cuopt/grpc/client/grpc_client.pyx:22-43]().

```mermaid
graph TD
    subgraph Natural Language Space
        A[""Python Application""] --> B[""Job Status Polling Loop""]
        B --> C[""Log & Incumbent Callbacks""]
    end
    subgraph Code Entity Space
        D[""cuopt::cython::grpc_python_client_t"""] --> E[""_wait_poll_loop()""]
        E --> F[""_invoke_log_callback()""]
    end
    A -.-> D
    B -.-> E
    C -.-> F
```
*Diagram: Python job lifecycle management through `grpc_python_client_t`.*

- **GIL Management**: Python-side polling (`_wait_poll_loop`) executes `time.sleep` in Python, releasing the GIL between short status RPCs so concurrent background threads (such as log or incumbent streams) remain responsive [python/cuopt/cuopt/grpc/client/grpc_client.pyx:101-131]().

Sources: `[cpp/include/cuopt/grpc/cython_grpc_client.hpp:121-202]()`, `[python/cuopt/cuopt/grpc/client/grpc_client.pyx:79-154]()`

---

## 4. Routing gRPC Client Integration

The routing client arm utilizes the same underlying `grpc_python_client_t` structure but targets Vehicle Routing Problem (VRP) payloads. 

- Problems are defined using `cpu_routing_problem_t` [cpp/src/grpc/client/grpc_client.hpp:12]() and submitted via `submit_vrp` [cpp/include/cuopt/grpc/cython_grpc_client.hpp:166-167]() using unary request structures.
- Solutions are retrieved and unpacked into `cpu_routing_solution_t` via `result_vrp` [cpp/include/cuopt/grpc/cython_grpc_client.hpp:171-172]().

Sources: `[cpp/include/cuopt/grpc/cython_grpc_client.hpp:166-172]()`, `[python/cuopt/cuopt/grpc/client/grpc_client.pyx:1-20]()`

---

## 5. Transport Security and TLS Configuration

Client connections support unencrypted transport, server-side TLS, or mutual TLS (mTLS) configured via `TlsConfig` and mapped to `grpc_python_client_connect_options_t` [python/cuopt/cuopt/grpc/client/grpc_client.pyx:175-199]().

```cpp
// Modes defined in C++ cython_grpc_client.hpp
enum class grpc_python_tls_mode_t : int {
  ENV      = 0,
  DISABLED = 1,
  EXPLICIT = 2,
};
```

- **PEM Resolution**: The `_load_pem` helper accepts raw PEM string text or file paths containing certificates/keys [python/cuopt/cuopt/grpc/client/grpc_client.pyx:164-173]().

Sources: `[python/cuopt/cuopt/grpc/client/grpc_client.pyx:164-199]()`, `[cpp/src/grpc/client/cython_grpc_client.cpp:53-73]()`

---

## 6. HTTP Proxy Webserver Bridge (`cuopt_server`)

The `cuopt_server` FastAPI application acts as a REST-to-gRPC proxy, translating incoming HTTP JSON/MessagePack requests into gRPC calls executed by `_grpc_client` and `_routing_client` [python/cuopt_server/cuopt_server/proxy_webserver.py:115-186]().

- **Async Status Polling**: Managed POST requests poll job statuses asynchronously from the FastAPI event loop rather than blocking thread pool workers with synchronous waits, ensuring health check endpoints remain responsive [python/cuopt_server/cuopt_server/proxy_webserver.py:139-145]().

Sources: `[python/cuopt_server/cuopt_server/proxy_webserver.py:115-186]`, `[python/cuopt_server/cuopt_server/tests/test_grpc_http_proxy.py:195-238]()`

---

