<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/buffa · page 8 Performance and Benchmarks · fetched 2026-10-26 -->

# Performance and Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [benchmarks/buffa/Cargo.lock](benchmarks/buffa/Cargo.lock)
- [benchmarks/buffa/benches/protobuf.rs](benchmarks/buffa/benches/protobuf.rs)
- [benchmarks/datasets/packed_signed.pb](benchmarks/datasets/packed_signed.pb)
- [benchmarks/gen-datasets/Cargo.lock](benchmarks/gen-datasets/Cargo.lock)
- [benchmarks/gen-datasets/src/main.rs](benchmarks/gen-datasets/src/main.rs)
- [benchmarks/history/README.md](benchmarks/history/README.md)
- [benchmarks/history/REPORT.md](benchmarks/history/REPORT.md)
- [benchmarks/history/annotations.md](benchmarks/history/annotations.md)
- [benchmarks/history/charts/compute_size.svg](benchmarks/history/charts/compute_size.svg)
- [benchmarks/proto/bench_messages.proto](benchmarks/proto/bench_messages.proto)

</details>



This section provides an overview of the performance characteristics of `buffa`, the methodology used for cross-implementation benchmarking, and the stress-testing infrastructure used to validate the compiler at scale.

`buffa` is designed for high-throughput serialization and deserialization. Key architectural choices that drive its performance include:
- **Linear-time serialization**: By using a two-pass model where message sizes are pre-calculated and stored in a `SizeCache` field [buffa/src/lib.rs:19-20](), `buffa` avoids the $O(N^2)$ complexity common in libraries that re-calculate nested sizes during the write phase.
- **Zero-copy Deserialization**: The `MessageView<'a>` trait [buffa/src/lib.rs:431-431]() and generated view types allow for borrowing string and byte fields directly from the input buffer, eliminating heap allocations during the decode path.
- **`OwnedView<V>`**: A self-referential container that pairs a `Bytes` buffer with its view, allowing zero-copy data to be sent across thread boundaries while remaining `'static` [buffa/src/view/owned.rs:25-30]().
- **Layout Normalization**: To ensure benchmarks reflect code changes rather than instruction-cache luck, `buffa` uses 64-byte block and loop alignment (`-Cllvm-args=-align-all-nofallthru-blocks=6 -Cllvm-args=-align-loops=64`) during performance measurement [benchmarks/history/README.md:56-61]().

## Benchmark Suite

The `benchmarks/` workspace contains a comprehensive suite for comparing `buffa` against other popular Protobuf implementations and tracking `buffa`'s own performance across releases [benchmarks/history/README.md:3-7]().

The suite measures throughput (MiB/s) across representative message types defined in `bench_messages.proto` [benchmarks/proto/bench_messages.proto:1-7]():
- `ApiResponse`: Flat message with mixed scalars.
- `LogRecord`: String-heavy message testing allocation overhead.
- `AnalyticsEvent`: Deeply nested message testing recursive decode and `SizeCache`.
- `MediaFrame`: Binary-payload heavy message exercising `bytes` fields.
- `PackedTile`: Many small sub-messages with packed repeated scalars.

### Performance Characteristics
As of the latest benchmarks (v0.8.0), `buffa` shows the following characteristics:
- **Binary Decode (View)**: Zero-copy views significantly outperform owned codecs. `LogRecord` view decode reaches 1,670 MiB/s [benchmarks/history/REPORT.md:104-104]().
- **UTF-8 Optimization**: The introduction of `fast-utf8` (using `smoothutf8::verify_with_slack`) in v0.8.0 improved `decode_view` throughput on string-heavy shapes by 17–21% [benchmarks/history/annotations.md:33-36]().
- **Packed Field Efficiency**: v0.7.1 introduced packed-varint reservation optimizations, resulting in a ~47% jump in `PackedTile` decode performance [benchmarks/history/annotations.md:47-49]().

### Benchmark Architecture
The following diagram illustrates how the benchmark workspace is structured to bridge the gap between performance testing and the code entities being measured.

**Title: Benchmark Workspace Structure**
```mermaid
graph TD
    subgraph "Benchmarks Workspace [benchmarks/]"
        [bench-buffa] -- "depends on" --> [buffa_runtime]
        [bench-buffa] -- "depends on" --> [buffa-build]
        [bench-buffa] -- "runs" --> [protobuf_rs_bench]
    end

    subgraph "Data Sources [benchmarks/proto/]"
        [proto_files] --> [bench_messages_proto]
        [proto_files] --> [benchmarks_proto]
    end

    [protobuf_rs_bench] -- "measures" --> [Message::decode_from_slice]
    [protobuf_rs_bench] -- "measures" --> [MessageView::decode_view]
    [protobuf_rs_bench] -- "measures" --> [Message::compute_size]
    [protobuf_rs_bench] -- "measures" --> [serde_json::to_string]

    style [Message::decode_from_slice] stroke-dasharray: 5 5
    style [MessageView::decode_view] stroke-dasharray: 5 5
    style [Message::compute_size] stroke-dasharray: 5 5
```
Sources: [benchmarks/buffa/Cargo.lock:45-54](), [benchmarks/buffa/benches/protobuf.rs:27-82](), [benchmarks/proto/bench_messages.proto:14-110]()

### Cross-Implementation and History
`buffa` maintains a detailed history of performance across versions [benchmarks/history/REPORT.md:1-10](). This history is normalized for layout noise to isolate real code-driven regressions or improvements from compiler placement luck [benchmarks/history/annotations.md:13-19]().

For details on the benchmark datasets and the specific historical movements, see [Benchmark Suite](#8.1).

---

## Stress Test (googleapis)

To ensure the robustness of the `buffa-codegen` logic and the `protoc-gen-buffa` plugin, `buffa` employs a large-scale stress test using the `googleapis` repository. This test validates the compiler's ability to handle thousands of `.proto` files and complex cross-package imports.

### Validation Pipeline
The stress test validates correctness at scale by generating Rust code for the entire Google Cloud API surface and ensuring it compiles successfully with `rustc`. This process serves as a critical regression test for the `buffa-codegen` crate's feature resolution and module tree generation logic.

For details on the stress test configuration and how to run it locally, see [Stress Test (googleapis)](#8.2).

### Stress Test Flow
The diagram below maps the stress test stages to the specific tools and code generators involved.

**Title: Google Cloud APIs Stress Test Pipeline**
```mermaid
graph LR
    subgraph "Input Space"
        [googleapis_protos] -- "proto files" --> [buf_generate]
    end

    subgraph "Codegen Space"
        [buf_generate] -- "invokes" --> [protoc-gen-buffa]
        [protoc-gen-buffa] -- "uses" --> [buffa_codegen_lib]
        [protoc-gen-buffa] -- "outputs" --> [generated_rust_files]
    end

    subgraph "Validation Space"
        [generated_rust_files] -- "aggregated into" --> [module_tree]
        [module_tree] -- "validated by" --> [cargo_check]
    end
```
Sources: [benchmarks/gen-datasets/src/main.rs:20-34](), [benchmarks/buffa/benches/protobuf.rs:6-17]()

---

**Related Pages:**
- [Benchmark Suite](#8.1)
- [Stress Test (googleapis)](#8.2)

---

