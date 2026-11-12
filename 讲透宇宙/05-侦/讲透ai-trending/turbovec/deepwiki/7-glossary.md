<!-- source: DeepWiki mcp.deepwiki.com · repo RyanCodrai/turbovec · page 7 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [docs/api.md](docs/api.md)
- [docs/recall_d1536.svg](docs/recall_d1536.svg)
- [docs/recall_d3072.svg](docs/recall_d3072.svg)
- [docs/recall_glove.svg](docs/recall_glove.svg)
- [turbovec-python/python/turbovec/__init__.py](turbovec-python/python/turbovec/__init__.py)
- [turbovec-python/python/turbovec/_interruptible.py](turbovec-python/python/turbovec/_interruptible.py)
- [turbovec-python/python/turbovec/_persist.py](turbovec-python/python/turbovec/_persist.py)
- [turbovec-python/src/lib.rs](turbovec-python/src/lib.rs)
- [turbovec-python/tests/test_interruptible.py](turbovec-python/tests/test_interruptible.py)
- [turbovec-python/tests/test_persist.py](turbovec-python/tests/test_persist.py)
- [turbovec/src/encode.rs](turbovec/src/encode.rs)
- [turbovec/src/id_map.rs](turbovec/src/id_map.rs)
- [turbovec/src/io.rs](turbovec/src/io.rs)
- [turbovec/src/io_v7.rs](turbovec/src/io_v7.rs)
- [turbovec/src/kernel_tests.rs](turbovec/src/kernel_tests.rs)
- [turbovec/src/lib.rs](turbovec/src/lib.rs)
- [turbovec/src/rotation.rs](turbovec/src/rotation.rs)
- [turbovec/src/search.rs](turbovec/src/search.rs)
- [turbovec/tests/adversarial_durability.rs](turbovec/tests/adversarial_durability.rs)
- [turbovec/tests/adversarial_durability_edges.rs](turbovec/tests/adversarial_durability_edges.rs)
- [turbovec/tests/adversarial_durability_fuzz.rs](turbovec/tests/adversarial_durability_fuzz.rs)
- [turbovec/tests/adversarial_durability_round2.rs](turbovec/tests/adversarial_durability_round2.rs)
- [turbovec/tests/adversarial_gen_reuse.rs](turbovec/tests/adversarial_gen_reuse.rs)
- [turbovec/tests/adversarial_load_memory.rs](turbovec/tests/adversarial_load_memory.rs)
- [turbovec/tests/calibration_bounds.rs](turbovec/tests/calibration_bounds.rs)

</details>



This page defines the technical terms, algorithms, and architectural concepts used within the `turbovec` codebase. It serves as a reference for onboarding engineers to understand the mathematical foundations, the v7 incremental persistence format, and the specific SIMD implementations that drive performance.

## Core Concepts

### TurboQuant (TQ)
The central algorithm, based on Google Research's data-oblivious quantization. It relies on the mathematical property that high-dimensional unit vectors, when randomly rotated, have coordinates that follow a predictable distribution [turbovec/src/lib.rs:3-5]().

### TQ+
An enhanced calibration layer that corrects for anisotropic data. It fits two parameters per coordinate—`shift` and `scale`—to map empirical quantiles onto codebook centroids [turbovec/src/encode.rs:10-24]().
*   **Calibration State:** An index is either `"uncalibrated"` or `"calibrated"` [docs/api.md:54-54]().
*   **Logic:** `fit_calibration` in [turbovec/src/encode.rs:205-280]().

### IdMapIndex
A wrapper providing stable external `u64` IDs. It uses a bidirectional `id ↔ slot` mapping to ensure IDs remain valid even when `swap_remove` reorders the underlying positional index [turbovec/src/id_map.rs:1-13]().

### TurboQuantIndex
The core positional index. Vectors are identified by their insertion slot (`0..n`). It manages `packed_codes`, `scales`, and the lazy initialization of SIMD caches [turbovec/src/lib.rs:61-81]().

---

## Algorithms and Mathematics

### Block-Hadamard Rotation
Replaces the expensive QR-based rotation. It uses a Walsh-Hadamard Transform (WHT) combined with permutations seeded by **ChaCha8** to achieve near-orthogonal rotation at $O(d \log d)$ complexity [turbovec/src/rotation.rs:1-20]().
*   **ROTATION_SEED:** A fixed constant ensuring deterministic rotation [turbovec/src/rotation.rs:22-22]().

### Lloyd-Max Scalar Quantization
Used to find optimal centroids and boundaries for the **Beta distribution** ($Beta(\frac{d-1}{2}, \frac{d-1}{2})$) [turbovec/src/codebook.rs:1-5]().
*   **Beta CDF:** Used during calibration to anchor TQ+ parameters [turbovec/src/encode.rs:32-32]().

### WHM (Weighted Harmonic Mean)
A metric used in the hillclimb benchmarks to balance speed and recall improvements [benchmarks/suite/LOG.md:1-20]().

---

## Data Layouts and SIMD

### Bit-Plane Packed Layout
The "cold" storage format. Bits for each coordinate are grouped into planes (e.g., all bit-0s for a block of vectors are contiguous) [turbovec/src/encode.rs:51-71]().

### Sequential Blocked Layout
The "hot" search format. Data is organized into **BLOCK** units (32 vectors) [turbovec/src/lib.rs:89-89]().
*   **perm0:** Interleaving for x86 AVX2 to handle 128-bit lane boundaries [turbovec/src/pack.rs:63-88]().
*   **Vector-Major:** Layout for VNNI/SDOT kernels.
*   **VM8:** A specific layout for ARM SMMLA kernels [turbovec/src/pack.rs:90-114]().

### SIMD Kernels
*   **AVX-512BW/VNNI/GFNI:** High-performance x86 kernels using byte-manipulation and neural-network instructions.
*   **NEON SDOT/SMMLA:** ARM kernels for dot-product and matrix-multiply acceleration.
*   **Nibble-Split LUT:** A technique where 4-bit scores are looked up via SIMD shuffle instructions (e.g., `vpshufb`) [turbovec/src/search.rs:1-10]().

---

## Persistence (v7 Container)

The v7 format supports **Incremental Sync**, writing only changed blocks [turbovec/src/io_v7.rs:1-13]().

### A/B Header Protocol
Two commit slots (`header A` and `header B`). A sync flips between them, ensuring that a crash during a header write leaves the previous commit intact [turbovec/src/io_v7.rs:19-26]().

### Redo Ops
Absolute writes stored in the header to represent removals or updates within a block without rewriting the whole block unit [turbovec/src/io_v7.rs:50-62]().

### Sync Management
*   **SyncCursor:** Tracks the state of a file on disk to determine what needs syncing [turbovec/src/io_v7.rs:320-350]().
*   **Nonce:** A unique `u64` identifying a file's lineage. **UNCLAIMED_NONCE** (0) marks a snapshot not yet bound to a sync cursor [turbovec/src/io.rs:156-166]().
*   **DeltaDigest:** A CRC-32C checksum covering the data blocks written in a specific sync [turbovec/src/io_v7.rs:39-49]().

**Persistence Flow**
```mermaid
graph TD
    subgraph "turbovec/src/io_v7.rs"
    A["Index State"] --> B["SyncSource::diff()"]
    B --> C["Write Block Units"]
    C --> D["Flip A/B Header"]
    D --> E["Update SyncCursor"]
    end
    
    subgraph "turbovec/src/io.rs"
    F["Atomic Replace Protocol"] --> G["Temp File Sibling"]
    G --> H["fsync + Rename"]
    end
```
Sources: [turbovec/src/io_v7.rs:1-84](), [turbovec/src/io.rs:14-28]()

---

## Domain Concepts

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Slot** | A positional index `0..n`. | [docs/api.md:16-16]() |
| **Handle** | A `u64` ID in `IdMapIndex`. | [turbovec/src/id_map.rs:6-13]() |
| **swap_remove** | O(1) deletion that moves the last vector into the hole. | [turbovec/src/lib.rs:142-151]() |
| **FLUSH_EVERY** | Threshold to prevent SIMD accumulator overflow. | [turbovec/src/lib.rs:102-102]() |
| **BATCH_CHUNK_SIZE** | Default size for interruptible Python operations. | [turbovec-python/python/turbovec/_interruptible.py:10-20]() |
| **JSON Fidelity** | Ensuring side-car JSONs match the `.tvim` index. | [turbovec-python/python/turbovec/_persist.py:1-22]() |
| **Torn Store** | A file corrupted by a partial write during a crash. | [turbovec/src/io.rs:140-143]() |
| **Outcome Unknown** | A state where a write was issued but its success is unconfirmed. | [turbovec/src/io_v7.rs:40-49]() |

---

## Search & Filtering

### Allowlist/Bitmask Filtering
Filters are applied inside the SIMD kernel. **block_has_allowed** short-circuits 32-vector blocks if no vectors in that block are permitted [README.md:82-88]().

### Similarity Modes
*   **Cosine:** Normalized dot product.
*   **Dot Product:** Raw inner product [docs/api.md:46-46]().

### Parallelism Gates
*   **SINGLE_QUERY_PARALLEL_MIN_BLOCKS:** Threshold (1024) where a single query starts using multiple threads [turbovec/src/search.rs:30-30]().
*   **mask-skip-counter:** Optimization to skip the filter check for dense allowlists [turbovec/src/lib.rs:44-50]().

**Natural Language to Code Mapping**
```mermaid
graph LR
    "Add Vectors" --> add["TurboQuantIndex::add()"]
    "Search" --> search["search::search()"]
    "Delete" --> remove["IdMapIndex::remove()"]
    "Persist" --> sync["TurboQuantIndex::sync()"]
    "Calibrate" --> calibrate["TurboQuantIndex::calibrate()"]

    subgraph "turbovec/src/lib.rs"
    add
    calibrate
    end
    subgraph "turbovec/src/id_map.rs"
    remove
    end
    subgraph "turbovec/src/search.rs"
    search
    end
    subgraph "turbovec/src/io_v7.rs"
    sync
    end
```
Sources: [turbovec/src/lib.rs:1-100](), [turbovec/src/id_map.rs:1-37](), [turbovec/src/search.rs:1-30](), [turbovec/src/io_v7.rs:1-100]()