<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/buffa · page 2 Core Runtime (`buffa`) · fetched 2026-10-26 -->

# Core Runtime (`buffa`)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.changes/unreleased/changed-20260627-000610.yaml](.changes/unreleased/changed-20260627-000610.yaml)
- [CHANGELOG.md](CHANGELOG.md)
- [buffa-codegen/src/owned_view.rs](buffa-codegen/src/owned_view.rs)
- [buffa-descriptor/src/reflect/containers.rs](buffa-descriptor/src/reflect/containers.rs)
- [buffa-test/src/tests/owned_view.rs](buffa-test/src/tests/owned_view.rs)
- [buffa/src/map_codec.rs](buffa/src/map_codec.rs)
- [buffa/src/message.rs](buffa/src/message.rs)
- [buffa/src/message_field.rs](buffa/src/message_field.rs)
- [buffa/src/types.rs](buffa/src/types.rs)
- [docs/guide.md](docs/guide.md)
- [protoc-gen-buffa/src/main.rs](protoc-gen-buffa/src/main.rs)

</details>



The `buffa` crate is the core runtime library that provides the foundational traits, types, and serialization logic required by all generated code. It is designed for high performance, offering both standard owned message types and zero-copy "view" types. The runtime supports `no_std` environments (requiring `alloc`) and provides first-class support for Protobuf Editions. [buffa/src/lib.rs:1-10]()

### Architecture Overview

The runtime is structured to separate the high-level message interface from the low-level wire format primitives. Generated messages implement the `Message` trait, which coordinates with the `encoding` module to perform two-pass serialization (size calculation followed by writing). [buffa/src/message.rs:1-63]() In version 0.8.0, the runtime introduced pluggable owned representations for all field kinds, allowing users to substitute `String`, `Vec<u8>`, or `HashMap` with custom types like `SmolStr` or `SmallVec` via traits like `ProtoString` and `ProtoList`. [CHANGELOG.md:11-16](), [CHANGELOG.md:87-98]()

#### Core Component Relationships

This diagram shows how the core runtime entities interact during the lifecycle of a message, from raw bytes to a high-level Rust struct.

```mermaid
graph TD
    subgraph "InputSpace"
        ["&[u8] / Bytes"]
    end

    subgraph "buffa_Runtime_Entities"
        ["DecodeOptions"] -- "configures" --> ["Message"]
        ["Message"] -- "uses" --> ["encoding::*"]
        ["encoding::*"] -- "parses" --> ["WireType"]
        ["Message"] -- "populates" --> ["UnknownFields"]
        ["Message"] -- "contains" --> ["MessageField<T>"]
        ["Message"] -- "contains" --> ["EnumValue<E>"]
        ["Message"] -- "uses" --> ["SizeCachePool"]
    end

    subgraph "Generated_Code_Space"
        ["MyMessage (struct)"] -- "implements" --> ["Message"]
        ["MyEnum (enum)"] -- "implements" --> ["Enumeration"]
        ["MyMessageOwnedView"] -- "wraps" --> ["OwnedView"]
    end

    ["&[u8] / Bytes"] --> ["Message::decode_from_slice"]
    ["Message::decode_from_slice"] --> ["MyMessage (struct)"]
```
**Sources:** [buffa/src/lib.rs:91-106](), [buffa/src/message.rs:27-52](), [buffa/src/encoding.rs:28-35](), [CHANGELOG.md:42-45]()

---

### Key Runtime Modules

The `buffa` runtime is divided into several specialized modules, each handling a specific aspect of the Protobuf specification. [buffa/src/lib.rs:91-106]()

| Module | Description |
| :--- | :--- |
| `message` | Defines the `Message` trait, `DecodeOptions`, and `SizeCachePool`. |
| `view` | Provides the `MessageView` trait and `OwnedView` for zero-copy access. |
| `encoding` | Contains low-level primitives for varints, fixed-width types, and tags. |
| `enumeration` | Implements `EnumValue<E>` for open/closed enum semantics. |
| `message_field` | Provides `MessageField<T>` and the `ProtoBox` trait for pluggable pointers. |
| `map_codec` | Generic wire codec for `map<K, V>` fields and the `MapStorage` trait. |
| `types` | Protobuf scalar type encoding strategies and UTF-8 validation. |

**Sources:** [buffa/src/lib.rs:91-106](), [buffa/src/map_codec.rs:1-30](), [buffa/src/types.rs:1-29]()

---

### Message Trait and Wire Format Codec
The `Message` trait is the primary interface for interacting with generated owned types. It provides methods for encoding to `Vec<u8>` or `bytes::Bytes`, and decoding from slices or `std::io::Read` sources. [buffa/src/message.rs:27-111]() Serialization uses a two-pass model: `compute_size` populates a `SizeCache`, and `write_to` consumes it. [buffa/src/message.rs:166-170]() To optimize heap usage during encoding, `SizeCachePool` allows reuse of spill-buffer allocations. [CHANGELOG.md:42-53]()

For details, see [Message Trait and Wire Format Codec](#2.1).

**Sources:** [buffa/src/message.rs:78-150](), [buffa/src/encoding.rs:1-5](), [CHANGELOG.md:42-57]()

---

### Zero-Copy Views and OwnedView
To avoid allocations during decoding, `buffa` generates "View" types (e.g., `FooView<'a>`). These types implement the `MessageView` trait and borrow `string` and `bytes` fields directly from the source buffer. [buffa/src/lib.rs:52-66]() The `OwnedView` container allows these borrowed types to be stored as `'static` entities by bundling them with their backing `Bytes` buffer. [buffa/src/lib.rs:103-106]() Additionally, `buffa-codegen` emits `FooOwnedView` wrappers that provide per-field accessor methods over an `OwnedView`. [buffa-codegen/src/owned_view.rs:1-10]()

For details, see [Zero-Copy Views, OwnedView, and HasMessageView](#2.2).

**Sources:** [buffa/src/lib.rs:52-66](), [buffa/src/lib.rs:103-106](), [buffa-test/src/tests/owned_view.rs:1-8]()

---

### Enumerations, MessageField, and Oneof
The runtime provides specialized wrappers to handle Protobuf's unique field semantics. `EnumValue<E>` handles "open" enums by preserving unknown numeric values. [buffa/src/lib.rs:99]() `MessageField<T>` provides a `Deref` implementation to a default instance, simplifying access to optional sub-messages without excessive `Option` unwrapping. [buffa/src/lib.rs:98](), [buffa/src/message_field.rs:1-6]() It now includes `unwrap()` and `expect()` methods to consume the field directly. [CHANGELOG.md:37-41]()

For details, see [Enumerations, MessageField, and Oneof](#2.3).

**Sources:** [buffa/src/lib.rs:98-99](), [buffa/src/message_field.rs:1-17](), [CHANGELOG.md:37-41]()

---

### Extensions and Unknown Fields
Protobuf allows messages to be extended with additional fields not defined in the original message. `buffa` manages these via the `ExtensionSet`, which stores extension data within the `UnknownFields` collection. [buffa/src/lib.rs:100-102]() This ensures that unknown fields are preserved during round-trips. The runtime also enforces a `DEFAULT_UNKNOWN_FIELD_LIMIT` to prevent memory amplification attacks from untrusted input. [buffa/src/message.rs:27-45]()

For details, see [Extensions and Unknown Fields](#2.4).

**Sources:** [buffa/src/lib.rs:100-102](), [buffa/src/message.rs:27-45]()

---

### JSON Serialization
When the `json` feature is enabled, `buffa` supports the Proto3 JSON Mapping via `serde`. [buffa/src/lib.rs:73-74]() This includes specialized handling for well-known types (like `Timestamp` or `Duration`) and the ability to register custom types for `google.protobuf.Any` resolution. [buffa/src/lib.rs:143-145]() The JSON mapping also supports the new pluggable string types in map keys. [CHANGELOG.md:71-73]()

For details, see [JSON Serialization](#2.5).

**Sources:** [buffa/src/lib.rs:73-74](), [buffa/src/lib.rs:143-145](), [CHANGELOG.md:59-73]()

---

### Data Flow: From Wire to View
The following diagram illustrates the relationship between the raw input, the `MessageView` trait, and the `OwnedView` container, which bridges the gap between borrowed and owned lifetimes.

```mermaid
graph LR
    subgraph "Memory_Heap_Stack"
        ["RawBytes [u8]"]
    end

    subgraph "View_Layer"
        ["MessageView"] -- "borrows from" --> ["RawBytes [u8]"]
        ["MyMessageView<'a>"] -- "impl" --> ["MessageView"]
    end

    subgraph "Safe_Container"
        ["OwnedView<V>"] -- "holds" --> ["bytes::Bytes"]
        ["OwnedView<V>"] -- "references" --> ["MyMessageView<'static>"]
        ["OwnedView::reborrow"] -- "returns" --> ["MyMessageView<'b>"]
        ["MyMessageOwnedView"] -- "provides accessors for" --> ["OwnedView"]
    end

    ["RawBytes [u8]"] --> ["MessageView::decode_view"]
    ["bytes::Bytes"] --> ["OwnedView::new"]
```
**Sources:** [buffa/src/lib.rs:52-66](), [buffa/src/lib.rs:103-106](), [buffa-codegen/src/owned_view.rs:1-10]()

---

