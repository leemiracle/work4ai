<!-- source: DeepWiki mcp.deepwiki.com · repo roboflow/supervision · extra page CompactMask · fetched 2026-10-30 -->

# CompactMask

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/how_to/use_compact_masks.md](docs/how_to/use_compact_masks.md)
- [docs/notebooks/compact-mask-sam3.ipynb](docs/notebooks/compact-mask-sam3.ipynb)
- [examples/compact_mask/README.md](examples/compact_mask/README.md)
- [examples/compact_mask/benchmark.py](examples/compact_mask/benchmark.py)
- [examples/compact_mask/benchmark_nmm.py](examples/compact_mask/benchmark_nmm.py)
- [examples/compact_mask/requirements.txt](examples/compact_mask/requirements.txt)
- [src/supervision/detection/compact_mask.py](src/supervision/detection/compact_mask.py)
- [tests/detection/test_compact_mask.py](tests/detection/test_compact_mask.py)
- [tests/detection/test_compact_mask_union.py](tests/detection/test_compact_mask_union.py)
- [tests/detection/utils/test_masks.py](tests/detection/utils/test_masks.py)

</details>



## Purpose and Scope

`CompactMask` is a memory-efficient instance segmentation mask storage mechanism in `supervision` designed to bypass the prohibitive `O(N \cdot H \cdot W)` memory complexity of dense boolean arrays [src/supervision/detection/compact_mask.py:1-15](). High-resolution aerial imagery, satellite tiles, and dense crowd scenes with hundreds of objects frequently trigger `MemoryError` when stored as stacked `(N, H, W)` tensors [examples/compact_mask/README.md:1-17](). `CompactMask` stores each mask as a run-length encoding (RLE) scoped strictly to its bounding-box crop (`xyxy`), utilizing pre-existing detection bounding boxes without requiring extra metadata [src/supervision/detection/compact_mask.py:1-15]().

Sources: [src/supervision/detection/compact_mask.py:1-15](), [examples/compact_mask/README.md:1-17]()

---

## Architecture and Core Data Structures

The `CompactMask` class encapsulates four primary internal attributes to represent sparse masks over a shared canvas [src/supervision/detection/compact_mask.py:37-184]():
- `_rles`: A sequence of 1D `int32` numpy arrays storing column-major (F-order) run lengths [src/supervision/detection/compact_mask.py:37-146]().
- `_crop_shapes`: An `(N, 2)` `int32` array tracking the `(height, width)` of each bounding-box crop.
- `_offsets`: An `(N, 2)` `int32` array storing the `(x, y)` top-left coordinates of each crop relative to the full image.
- `_image_shape`: A tuple `(height, width)` defining the full canvas dimensions [src/supervision/detection/compact_mask.py:148-177]().

```mermaid
graph TD
    subcode ["Natural Language to Code Entity Space"]
    NL_Input[""Dense (N,H,W) Bool Array""] -->|CompactMask.from_dense| CM[""CompactMask Class (src/supervision/detection/compact_mask.py)""]
    NL_RLE[""COCO RLE Payload""] -->|CompactMask.from_coco_rle| CM
    CM --> RLES[""_rles (Sequence[NDArray[np.int32]])""]
    CM --> SHAPES[""_crop_shapes (NDArray[np.int32])""]
    CM --> OFFSETS[""_offsets (NDArray[np.int32])""]
    CM --> IMG_SHAPE[""_image_shape (tuple[int, int])""]
```
Sources: [src/supervision/detection/compact_mask.py:1-184](), [docs/how_to/use_compact_masks.md:29-61]()

---

## RLE Encoding and Internal Helpers

RLE operations in `supervision` use column-major (F-order) indexing to maintain compatibility with COCO formats (`pycocotools`) [examples/compact_mask/README.md:100-110](). The module implements several vectorised numerical helpers:

- `_rle_area(rle)`: Computes the number of `True` pixels directly from run lengths by summing alternate elements `rle[1::2]`, avoiding full array materialisation [src/supervision/detection/compact_mask.py:37-56]().
- `_rle_to_column_intervals(rle, crop_height, offset)`: Extracts foreground `(x, y_start, y_stop)` intervals in image coordinates, skipping background runs entirely to scale processing with active pixel density [src/supervision/detection/compact_mask.py:59-109]().
- `_rle_counts_int32(counts)`: Splits oversized run counts exceeding `np.int32` limits into alternating limit/zero pairs, preserving foreground/background bit parity [src/supervision/detection/compact_mask.py:111-146]().
- `_validate_uniform_image_shape(masks_list, action)`: Enforces that all collected or merged `CompactMask` instances share an identical `_image_shape`, raising `ValueError` upon mismatch [src/supervision/detection/compact_mask.py:148-178]().

Sources: [src/supervision/detection/compact_mask.py:37-178]()

---

## Union and Merge Semantics

Combining overlapping predictions, executing Non-Maximum Merging (`NMM`), or merging distinct `Detections` objects containing `CompactMask` instances relies on specialised sparse union algorithms [tests/detection/test_compact_mask_union.py:1-170]().

```mermaid
graph TD
    subcode2 ["Union Data Flow and Code Mapping"]
    InputDets[""Detections.merge / with_nmm""] --> Validate[""_validate_uniform_image_shape()""]
    Validate --> CheckDense[""_should_union_densely() Evaluates Run Ratio""]
    CheckDense -->|Sparse Path| ColIntervals[""_rle_to_column_intervals()""]
    ColIntervals --> Int32Split[""_rle_counts_int32()""]
    Int32Split --> ResultCM[""Merged CompactMask Output""]
    CheckDense -->|Dense Fallback Ratio > 0.5| DensePass[""Dense Crop Decoding Fallback""]
    DensePass --> ResultCM
```

When masks are highly fragmented (such as checkerboard patterns where the foreground-run to crop-area ratio exceeds `_DENSE_FALLBACK_RUN_RATIO = 0.5`), the engine falls back to a dense crop representation to avoid sort-cost overheads from interval unions [src/supervision/detection/compact_mask.py:180-184](). Otherwise, union calculations proceed entirely in RLE space without decoding the full-frame canvas [tests/detection/test_compact_mask_union.py:18-78]().

Sources: [src/supervision/detection/compact_mask.py:148-184](), [tests/detection/test_compact_mask_union.py:18-78]()

---

## Performance and Benchmarks

For high-resolution inputs (e.g., 4K imagery with 1,000 objects), dense boolean representations require gigabytes of memory, whereas `CompactMask` scales down to megabytes [examples/compact_mask/README.md:9-53]().

| Metric / Operation | Dense `(N, H, W)` | Crop-RLE (`CompactMask`) |
| :--- | :--- | :--- |
| **Memory (N=1,000, 4K canvas)** | ~8.3 GB | ~2 MB [examples/compact_mask/README.md:46-50]() |
| **Encode Time (N=1,000)** | O(1) (direct allocation) | O(A) scan crop rows [examples/compact_mask/README.md:56-64]() |
| **Crop-Only Decode** | O(1) (strided slice) | O(A) expand runs (~2 ms) [examples/compact_mask/README.md:75-87]() |
| **IoU / NMS Pre-filter** | Pairwise dense AND (~10,000 ms) | Bbox pre-filter + sparse intersection (~15 ms) [examples/compact_mask/README.md:88-96]() |

Sources: [examples/compact_mask/README.md:1-96]()

---

## Integration with Annotators and InferenceSlicer

`CompactMask` integrates directly into the `supervision` pipeline without changing public annotator signatures [docs/how_to/use_compact_masks.md:11-172]().

### Annotators and `requires_mask`
Annotators declare `requires_mask = False` by default (e.g., `BoxAnnotator`, `LabelAnnotator`) [docs/how_to/use_compact_masks.md:92-122](). When passing `Detections` containing `CompactMask` to non-mask annotators, users can strip or ignore the mask attribute to eliminate unnecessary decoding overhead [docs/how_to/use_compact_masks.md:92-122](). Mask-aware annotators like `MaskAnnotator` and `PolygonAnnotator` (`requires_mask = True`) consume `CompactMask` directly by rendering via crop-scoped bounding box regions rather than materialising full frames [docs/how_to/use_compact_masks.md:92-126]().

### Inference Integration
`InferenceSlicer` and `Detections.from_inference()` accept a `compact_masks=True` argument [docs/how_to/use_compact_masks.md:65-88](). This routes incoming COCO RLE dictionaries directly through `CompactMask.from_coco_rle()`, avoiding intermediate boolean tensor allocations [docs/how_to/use_compact_masks.md:65-88](). Similarly, calling `Detections.merge()` with mixed dense numpy arrays and `CompactMask` objects automatically coerces dense inputs into compact representations [docs/how_to/use_compact_masks.md:129-168]().

Sources: [docs/how_to/use_compact_masks.md:11-172]()

---

