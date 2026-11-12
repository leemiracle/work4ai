<!-- source: DeepWiki mcp.deepwiki.com · repo RyanCodrai/turbovec · page 3 Python Bindings and API · fetched 2026-10-30 -->

# Python Bindings and API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [turbovec-python/python/turbovec/__init__.py](turbovec-python/python/turbovec/__init__.py)
- [turbovec-python/python/turbovec/_interruptible.py](turbovec-python/python/turbovec/_interruptible.py)
- [turbovec-python/src/lib.rs](turbovec-python/src/lib.rs)
- [turbovec-python/tests/test_interruptible.py](turbovec-python/tests/test_interruptible.py)

</details>



The `turbovec` Python package provides a high-performance interface to the core Rust vector search engine. It leverages **PyO3** and **maturin** to bridge the gap between Rust's SIMD-optimized kernels and the Python data science ecosystem, specifically targeting seamless integration with **NumPy**, **LangChain**, **LlamaIndex**, **Haystack**, and **Agno**.

The package is structured as a hybrid: a compiled Rust extension module (`_turbovec`) handles the heavy lifting of quantization and search, while a pure Python layer provides high-level abstractions, interruptible batching, and framework integrations.

### System Architecture: Python to Rust Bridge

The following diagram illustrates how Python calls traverse the boundary into the Rust core, utilizing PyO3 for class wrapping and the `numpy` crate for zero-copy views.

**Interface Mapping: Python Space to Rust Entities**
```mermaid
graph LR
    subgraph "Python Space (turbovec)"
        [turbovec.TurboQuantIndex] -- "calls" --> [turbovec._turbovec]
        [turbovec.IdMapIndex] -- "calls" --> [turbovec._turbovec]
        [turbovec._interruptible.py] -- "wraps" --> [turbovec._turbovec]
    end

    subgraph "Rust Space (turbovec-python/src/lib.rs)"
        [turbovec._turbovec] -- "impl #[pyclass]" --> [TurboQuantIndex_Wrapper]
        [turbovec._turbovec] -- "impl #[pyclass]" --> [IdMapIndex_Wrapper]
        [TurboQuantIndex_Wrapper] -- "delegates" --> [turbovec::TurboQuantIndex]
    end

    subgraph "Data Interop (NumPy)"
        [numpy.ndarray_f32] -- "PyReadonlyArray2" --> [extract_f32_2d]
        [numpy.ndarray_u64] -- "PyReadonlyArray1" --> [extract_u64_1d]
        [extract_f32_2d] -- "view" --> [TurboQuantIndex_Wrapper]
    end
```
**Sources:** [turbovec-python/src/lib.rs:56-62](), [turbovec-python/src/lib.rs:65-71](), [turbovec-python/python/turbovec/__init__.py:1-22]()

---

### Low-Level Extension Module (`_turbovec`)

The core of the Python package is the `_turbovec` module, a compiled extension defined in Rust. It wraps the primary `TurboQuantIndex` and `IdMapIndex` structs from the core library.

The extension provides:
*   **Direct Memory Access**: Efficiently reads NumPy arrays via `PyReadonlyArray` [turbovec-python/src/lib.rs:4-7]().
*   **GIL Management**: Releases the Global Interpreter Lock (GIL) during long-running search and add operations to allow Python multi-threading.
*   **Fork-Safety**: Implements `pthread_atfork` handlers and a `FORK_GENERATION` counter to ensure the internal Rayon thread pool is safely re-initialized after a process fork.
*   **Strict Validation**: Custom error handlers like `extract_size` [turbovec-python/src/lib.rs:153-175]() and `mask_bytes` [turbovec-python/src/lib.rs:109-130]() provide clear Python exceptions for invalid dtypes or non-contiguous memory.

For a detailed breakdown of the PyO3 implementation, GIL discipline, and thread-pool management, see [PyO3 Extension Module (_turbovec)](#3.1).

**Sources:** [turbovec-python/src/lib.rs:1-130](), [turbovec-python/src/lib.rs:153-175]()

---

### Interruptible Chunking

Python delivers signals (like `Ctrl-C`) on the main thread. If that thread is parked inside a long Rust kernel call, the signal is queued until the call returns. `turbovec` solves this via a Python-side utility layer in `_interruptible.py` [turbovec-python/python/turbovec/_interruptible.py:1-80]().

*   **BATCH_CHUNK_SIZE**: A default slice size (4096) [turbovec-python/python/turbovec/__init__.py:18]() used to split large batches.
*   **Signal Servicing**: Control returns to Python between slices, allowing `KeyboardInterrupt` to fire within milliseconds rather than seconds.
*   **Atomicity**: The `add` operation pre-validates the entire batch [turbovec-python/python/turbovec/_interruptible.py:50-61]() to ensure that mid-batch cancellations leave the index in a consistent, queryable state.

**Sources:** [turbovec-python/python/turbovec/_interruptible.py:1-80](), [turbovec-python/python/turbovec/__init__.py:18-22]()

---

### Package Structure and Distribution

The `turbovec` package follows a modern layout where the Rust logic in `src/` is paired with a Python utility layer in `python/`.

**Package Layout**
```mermaid
graph TD
    [turbovec-python/] --> [pyproject.toml]
    [turbovec-python/] --> [Cargo.toml]
    [turbovec-python/] --> [src/lib.rs]
    [turbovec-python/] --> [python/turbovec/]
    
    [python/turbovec/] --> [__init__.py]
    [python/turbovec/] --> [_interruptible.py]
    [python/turbovec/] --> [_persist.py]
    [python/turbovec/] --> [langchain/]
    [python/turbovec/] --> [llama_index/]
    [python/turbovec/] --> [haystack/]
    [python/turbovec/] --> [agno/]
```

Key aspects of the distribution include:
*   **Maturin Build System**: Used as the PEP 517 build backend.
*   **Optional Dependencies**: Managed via `pyproject.toml` extra groups (e.g., `langchain`, `haystack`) for framework integrations.
*   **Persistence Utilities**: `_persist.py` provides atomic save logic and JSON fidelity guards for metadata side-cars.

For details on the build lifecycle and utility layer, see [Python Package Structure, Utilities, and Build](#3.2).

**Sources:** [turbovec-python/python/turbovec/__init__.py:1-48](), [turbovec-python/python/turbovec/_interruptible.py:82-150]()

---

