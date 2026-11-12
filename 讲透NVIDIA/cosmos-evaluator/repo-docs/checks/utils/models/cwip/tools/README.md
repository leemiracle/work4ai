# CWIP - Tools
Contains command line tools for working with the CWIP model.

The CWIP model weights (`config.json` + `model.safetensors`) live in-tree at
`checks/utils/models/cwip/checkpoints/` and are tracked via Git LFS. Run `git lfs pull` after cloning to
materialize `model.safetensors` locally. There is no longer a download-from-registry step.

## `inference.py`
Load a CWIP model saved in HuggingFace format and optionally run inference on a camera/world video pair or on dummy inputs. Supports two loader backends (`--use_hf` selects between them) and opt-in multi-GPU + memory-layout accelerators.

```bash
usage: inference.py [--model_path MODEL_PATH] [--device DEVICE]
                    [--test_inference]
                    [--camera_video_path CAMERA_VIDEO_PATH]
                    [--world_video_path WORLD_VIDEO_PATH]
                    [--output_dir OUTPUT_DIR]
                    [--batch_size BATCH_SIZE]
                    [--tp_size TP_SIZE] [--fp_size FP_SIZE]
                    [--true_cp_size TRUE_CP_SIZE] [--sequence_parallel]
                    [--channels_last] [--use_hf] [--camera_only_mode]
                    [--image_size IMAGE_SIZE]
                    [--save_presence_masks]
                    [--presence_source {similarity,type,union,intersection}]
                    [--type_mask_gate {confidence,argmax}]
                    [--type_confidence_threshold TYPE_CONFIDENCE_THRESHOLD]
                    [--per_class_thresholds PER_CLASS_THRESHOLDS]
```

Arguments:
- `--model_path`: Path to the HuggingFace-format model directory (e.g., `checks/utils/models/cwip/checkpoints`); if omitted, uses the in-tree Git LFS checkpoint resolved from Bazel runfiles.
- `--device`: Device to load the model on (`cuda` by default).
- `--test_inference`: Run a quick forward pass on dummy data (if no videos provided).
- `--camera_video_path`: Path to camera video for real inference (optional).
- `--world_video_path`: Path to world video for real inference (optional).
- `--output_dir`: Directory to write visualizations from inference (optional).
- `--batch_size`: Batch size for inference to avoid OOM; reduce if running out of GPU memory (default: 10).
- `--tp_size`: Tensor-parallel world size; requires a multi-process launcher with `tp_size` ranks (default: 1).
- `--fp_size`: Frame-parallel size — scatter/gather frames across GPUs (default: 1).
- `--true_cp_size`: True context-parallel degree (Megatron CP = `fp_size × true_cp_size`); if unset, read from `config.json`.
- `--sequence_parallel`: Enable Megatron sequence parallelism; requires `--tp_size > 1`.
- `--channels_last`: Convert the loaded model + image inputs to `torch.channels_last`. Shape-independent; helps conv-heavy encoder stems on Ampere+ GPUs by ~5–15%. CUDA only.
- `--use_hf`: Load via `transformers.PreTrainedModel.from_pretrained` instead of the legacy custom loader. Requires the `transformers` package (already declared as a Bazel dep of the `cwip` py_library). Both backends consume the same on-disk layout (`config.json` + `model.safetensors`).
- `--camera_only_mode`: Load the full two-branch checkpoint but run **only** the camera branch (camera encoder/aligner, camera global embedding, and object-type prediction). The world encoder and the similarity head are skipped at forward time (no world FLOPs / activations). In video mode only `--camera_video_path` is required — `--world_video_path` is ignored and a black world tensor is synthesized solely so visualization tiling has a reference frame. In `--test_inference` mode no dummy world tensor is built. Requires a checkpoint whose object-type path is self-attention only (`patch_classifier.cross_attn_frequency=None`, which is the case for `use_separate_necks=True`); otherwise loading raises a clear `ValueError`.
- `--image_size`: Optional resize target as `H,W` (or a single int for a square) applied to decoded frames before the forward pass. `forward` derives its processing resolution from the input shape, so this directly bounds patch-former memory. Recommended for `--camera_only_mode` at native camera resolution: the two-branch path resizes the camera down to the world frame size, but camera-only has no world frame and otherwise runs at full camera resolution (e.g. the 1080×1920 sample), which is memory-heavy.
- `--save_presence_masks`: In video mode, also write the static object check's presence masks to `--output_dir` (see [Presence masks](#presence-masks---save_presence_masks)). Requires `--camera_video_path`, `--output_dir`, and either `--world_video_path` or `--camera_only_mode`. The four flags below take effect only with it; passing one without it is an error.
- `--presence_source`: How a two-stream run builds the masks: `similarity` (MATCH / EXTRA similarity labels), `type` (the type-head mask for both), `union` (default) / `intersection` (similarity label OR / AND the type-head mask). Ignored with `--camera_only_mode`, which always uses the type-head mask.
- `--type_mask_gate`: How the type-head mask is built: `confidence` (default; a patch is present when its top type probability is at least `--type_confidence_threshold`) or `argmax` (every patch present).
- `--type_confidence_threshold`: Minimum top type probability for the type-head mask, in `[0, 1]` (default: 0.5).
- `--per_class_thresholds`: Per-class overrides of `--type_confidence_threshold`, as comma-separated `ObjectType=threshold` pairs (names case-insensitive), e.g. `TRAFFIC_LIGHT_RED=0.7,HDMAP_TRAFFIC_SIGNS=0.6`. An override applies to patches whose predicted class is that type.

Make sure to source the `tools/env_setup.sh` script to setup the build environment before running the inference script:
```bash
. tools/env_setup.sh  # Note the whitespace between the . and the filepath
```
For details on environment setup, please refer to the [Getting Started Guide](../../../../../docs/getting_started.md). NOTE that you may need to restart docker to make some changes to take effect.
```bash
docker stop cosmos_eval && docker rm cosmos_eval
```

Examples (Bazel):
- Use the in-tree Git LFS checkpoint (resolved automatically from runfiles):
```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --device cuda \
  --test_inference
```

- Point at an explicit checkpoint directory:
```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --test_inference
```

- Run on a video pair:
```bash
cd /path/to/cosmos_evaluator/repository
PATH_TO_REPO=$(pwd)
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path ${PATH_TO_REPO}/checks/utils/models/cwip/checkpoints \
  --device cuda \
  --world_video_path ${PATH_TO_REPO}/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4 \
  --camera_video_path ${PATH_TO_REPO}/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --output_dir $(pwd)/tmp/cwip_inference
```

- **Camera-only mode** (`--camera_only_mode`): run just the camera embedding + object-type path, skipping the world encoder and the similarity head. Only a camera video is needed; in video mode this emits the object-type visualization subset only (see the table note below).
```bash
cd /path/to/cosmos_evaluator/repository
PATH_TO_REPO=$(pwd)
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path ${PATH_TO_REPO}/checks/utils/models/cwip/checkpoints \
  --device cuda \
  --camera_only_mode \
  --camera_video_path ${PATH_TO_REPO}/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --output_dir $(pwd)/tmp/cwip_inference \
  --image_size 720,1280  # camera-only has no world frame to resize to; bound patch-former memory (native 1080x1920 is heavy)

# or a quick dummy forward:
dazel run //checks/utils/models/cwip/tools:inference -- \
  --device cuda \
  --test_inference \
  --camera_only_mode
```

- **Presence masks** (`--save_presence_masks`): write the masks the static object check would score against, here the union of the similarity verdict and the type-head mask with stricter traffic-light and traffic-sign thresholds.
```bash
cd /path/to/cosmos_evaluator/repository
PATH_TO_REPO=$(pwd)
dazel run //checks/utils/models/cwip/tools:inference -- \
  --device cuda \
  --world_video_path ${PATH_TO_REPO}/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4 \
  --camera_video_path ${PATH_TO_REPO}/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --output_dir $(pwd)/tmp/cwip_inference \
  --save_presence_masks \
  --presence_source union \
  --per_class_thresholds TRAFFIC_LIGHT_RED=0.7,TRAFFIC_LIGHT_YELLOW=0.7,TRAFFIC_LIGHT_GREEN=0.7,TRAFFIC_LIGHT_UNKNOWN=0.7,HDMAP_TRAFFIC_SIGNS=0.6
```

- **HuggingFace `transformers` loader** (`--use_hf`): route the load through `CWIPInference.from_pretrained` (which calls `transformers.PreTrainedModel.from_pretrained` under the hood) instead of the legacy custom loader. Useful for smoke-testing the HF integration path that ships when the model is published to the Hub.
```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --device cuda \
  --test_inference \
  --use_hf
```

- **`channels_last` memory-layout accelerator**: opt-in, CUDA-only, shape-independent. Stacks with `--use_hf`.
```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --device cuda \
  --test_inference \
  --channels_last
```

- **Multi-GPU inference** (TP, FP, true CP) needs a multi-process launcher that sets distributed environment variables (`RANK`, `WORLD_SIZE`, `LOCAL_RANK`, etc.). The examples in `inference.py` use `torchrun --nproc_per_node=N`; `dazel run` typically starts a single process, so prefer `torchrun` (on host or in Docker) or another launcher (e.g. Slurm) that wires the same env. Flags: `--tp_size`, `--fp_size`, `--true_cp_size`, `--sequence_parallel`.

Behavior:
- Loads the CWIP model from `--model_path` (or the in-tree Git LFS checkpoint resolved from runfiles when omitted), prints model information and a detailed model summary.
- Loader backend: by default uses `CWIPInference.from_hf_format` (legacy custom loader; reads `config.json` + `model.safetensors` directly, no `transformers` import). Pass `--use_hf` to route through `CWIPInference.from_pretrained` (thin wrapper around `transformers.PreTrainedModel.from_pretrained`).
- TF32 fast path for residual fp32 matmuls is enabled unconditionally at startup via `torch.set_float32_matmul_precision("high")` (shape-independent and lossless for the bf16/fp16 model).
- If `--channels_last` is set on CUDA, converts the model to channels-last memory format and reshapes forward-pass image inputs to match. No-op on CPU.
- If videos are provided, preprocesses them, runs a forward pass, and writes visualizations to `--output_dir`.
- If `--test_inference` is set and no videos are provided, performs a dummy forward pass to verify the setup.
- If `--camera_only_mode` is set, the world encoder and similarity head are skipped: `forward` receives `world_image=None`, `world_global_features` / `world_spatial_features_list` / `patch_similarity_logits` are `None` in the output, and only the object-type visualization subset is written (see the table note below).

- If `--save_presence_masks` is set, also writes the static-check presence masks (see [Presence masks](#presence-masks---save_presence_masks)).

Visualization outputs (`--output_dir`, video mode only):

When both `--camera_video_path` and `--world_video_path` are passed, `inference.py` calls `CWIPInference.create_inference_visualizations(..., similarity_plots="radial", save_patch_data_dumps=False)` and writes seven files into `--output_dir`. The `_iter_NNNNNN` suffix is the iteration index (`000000` for one-shot CLI runs). Video encoding uses NVIDIA NVENC when available and falls back to CPU otherwise.

> **Camera-only mode (`--camera_only_mode`):** because the world encoder and similarity head are skipped, only the object-type subset is written — `tiled_video_iter_*.mp4` (camera-only layout: `[camera | backbone feature | aligned feature]`), `combined_patch_vis_iter_*.mp4` (2×2 type-only layout), and `detailed_patch_type_vis_iter_*.mp4`. The similarity outputs `similarity_radial_iter_*.png`, `class_percentage_radial_iter_*.png`, `class_pixel_count_radial_iter_*.png`, and `detailed_patch_similarity_vis_iter_*.mp4` are intentionally **not** produced.

| File | Format | Layout |
|---|---|---|
| `similarity_radial_iter_*.png` | 10×10 inch polar plot | One point per frame pair on a circle (angle = frame index, radius = `cos_sim + 1` so it stays in `[0, 2]`). Points colored by raw cosine similarity on a `coolwarm` colormap, connected by a line and filled to the center. Diagonal `(camera_i, world_i)` only — the off-diagonal similarity matrix is not rendered when `similarity_plots="radial"`. |
| `tiled_video_iter_*.mp4` | 2×2 grid video (3×2 when `camera_patch_features` is present) | Top row: camera frame, world frame. Bottom row: PCA-colorized last-layer spatial features for camera and world streams. The 3×2 variant adds a third row showing camera patch-classifier features. |
| `combined_patch_vis_iter_*.mp4` | 3×3 grid video (when both similarity and object-type heads ran; otherwise 2×3 or 2×2) | Rows 1–2 follow the 2×3 schema: row 1 = (camera, camera + similarity overlay, camera + object-type overlay); row 2 = (world, similarity prediction RGB, object-type prediction RGB). Row 3 is the **mask trio**: (camera × `MATCH+EXTRA` mask, the mask itself in grayscale, object-type prediction × mask) — "what type lives in each predicted-object pixel, weighted by confidence". With `--save_presence_masks` (two-stream), row 3 uses the static-check presence mask instead (correspondence OR hallucination mask, binary) and its labels read `Presence Mask (<settings>)`, e.g. `Presence Mask (presence_source=union, type_confidence>=0.5)`, `Cam x Presence`, `Type x Presence`; see [Presence masks](#presence-masks---save_presence_masks). |
| `class_percentage_radial_iter_*.png` | 12×12 inch polar plot | One closed curve per similarity class (`DONT_CARE`, `MATCH`, `WRONG`, `EXTRA`, `MISSING`); angle = frame index, radius = class percentage for that frame. Each class colored per `PatchSimilarityType2Color`. Average percentage shown in the legend. |
| `class_pixel_count_radial_iter_*.png` | 12×12 inch polar plot | Same radial layout as the percentage plot, but radius is the absolute per-class pixel count per frame (axis upper bound rounded up to the next hundred). |
| `detailed_patch_similarity_vis_iter_*.mp4` | 3×3 grid video | One subplot per similarity class (5 classes) plus camera/world reference frames, each showing the per-pixel probability map (sigmoid by default) over time. Subplot resolution defaults to 1280×720, dialed down to 640×360 when the layout would otherwise exceed NVENC's 4096×2160 limit. |
| `detailed_patch_type_vis_iter_*.mp4` | 5×6 grid video (30 tiles, fixed) | Row 1 = (camera, world, argmax overlay, class-0 prob, class-1 prob, class-2 prob); rows 2–5 = remaining per-class probability maps and empty padding. The exact class count is `patch_type_logits.shape[1]`, which depends on `object_type_class_mapping`: **18 for `v4`** (the bundled v1.0.1 checkpoint). Padding tiles are blank when the model has fewer than 23 classes. To stay within NVENC's 4096×2160 limit at this grid size, the per-subplot resolution is fixed at 640×360. |

Notes:
- GPU (`cuda`) is recommended and used by default when available.
- When `--model_path` is omitted, the in-tree Git LFS checkpoint at `checks/utils/models/cwip/checkpoints/` is used (resolved from Bazel runfiles). Run `git lfs pull` after cloning to ensure `model.safetensors` is materialized.
- When using `--model_path`, you can point to any local HuggingFace-format checkpoint directory.

### Presence masks (`--save_presence_masks`)

The static object check reads CWIP through two per-patch presence masks per frame: correspondence scores the mask where
the ground truth projects an object, and hallucination scores it where nothing projects. `--save_presence_masks` writes
those masks so a setting can be inspected on a clip before it is used in the check. The flags mirror the check's objects
config:

| Flag | Objects config key |
|---|---|
| `--presence_source` | `presence.source` |
| `--type_mask_gate` | `presence.type_mask.gate` |
| `--type_confidence_threshold` | `presence.type_mask.confidence_threshold` |
| `--per_class_thresholds` | `presence.type_mask.per_class_thresholds` |

`--per_class_thresholds` is keyed by `ObjectType` name. The config key is keyed by object class name instead, and one
class can cover several types: `traffic_light` covers `TRAFFIC_LIGHT_RED`, `TRAFFIC_LIGHT_YELLOW`, `TRAFFIC_LIGHT_GREEN`,
and `TRAFFIC_LIGHT_UNKNOWN`, `traffic_sign` is `HDMAP_TRAFFIC_SIGNS`. An `ObjectType` that the model's class mapping
ignores is rejected.

| `--presence_source` | Correspondence mask | Hallucination mask |
|---|---|---|
| `similarity` | similarity label MATCH (WRONG counts as MATCH) | similarity label EXTRA |
| `type` | type-head mask | type-head mask |
| `union` (default) | MATCH OR type-head mask | EXTRA OR type-head mask |
| `intersection` | MATCH AND type-head mask | EXTRA AND type-head mask |

With `--camera_only_mode` there is no similarity head, so both masks are the type-head mask whatever `--presence_source`
says. Patches the type head predicts as background are cleared from both masks: the check keeps only patches
whose predicted type is the class it is checking, so a background patch never counts, while the type-head mask marks
confident background (sky, road surface) present.

The tool and the check apply the same source and gate logic ([`modules/presence.py`](../modules/presence.py)); the
tool's mask computation and visualization live in
[`visualization/presence_vis.py`](../visualization/presence_vis.py). The masks approximate the check's rather than
reproduce them: the tool gates at the model's patch resolution, while the check gates the type logits after bilinearly
resizing them to the video frame size; the tool clears background patches, while the check keeps only the patches of
the class it is checking; and `--per_class_thresholds` is keyed by `ObjectType`, the check's config by object class.

In a two-stream run the flag also switches row 3 of `combined_patch_vis_iter_*.mp4` from the soft similarity mask
(`clamp(P(MATCH) + P(WRONG) + P(EXTRA), 0, 1)`) to the presence mask the check uses, the union of the correspondence and
hallucination masks, and names the selected settings in that row's labels (`Presence Mask (presence_source=union,
type_confidence>=0.5)`, `Cam x Presence`, `Type x Presence`). Camera-only runs render the type-only 2×2 layout, which has no row 3.

A presence mask is the union of the correspondence and hallucination masks: the patches either check counts as present.
Besides the presence mask under the selected flags, the outputs contrast two masks. Two-stream, these are the similarity
mask (the `similarity` source) and the type-head mask under the selected type-head flags, the two inputs `union` and
`intersection` combine. Camera-only, which has no similarity head, they are the type-head mask at the default settings
(`confidence` gate at 0.5, no per-class overrides) and under the selected flags, showing what `--type_mask_gate`,
`--type_confidence_threshold`, and `--per_class_thresholds` change.

The flag adds three files to `--output_dir` (`NNNNNN` is the iteration index, `000000` for CLI runs):

| File | Contents |
|---|---|
| `presence_masks_iter_NNNNNN.npz` | `(frames, h, w)` `uint8` 0/1 masks at the patch resolution: `presence` (under the selected flags), `correspondence` and `hallucination` (its per-check masks), and the two contrasted masks: `similarity_presence` and `type_presence` two-stream, `default_type_presence` and `type_presence` camera-only. |
| `presence_summary_iter_NNNNNN.json` | The settings used (`mode`, `presence_source` (`type` in camera-only mode, as in the check's results), `presence` and `compared` (the labels shown in the video), the type-head settings), the mask shape, and the fraction of patches per frame and on average in `presence`, each contrasted mask (`<name>_presence`), each contrasted mask alone (`<name>_only`, e.g. `similarity_only` / `type_only`), and both (`both`). |
| `presence_mask_vis_iter_NNNNNN.mp4` | 2×2 grid, each panel at most 960 px wide and labeled by a legend in its top-left corner. Left column: the presence mask under the selected flags in cyan, tinted onto the camera (top) and alone on black (bottom); the legend names the settings, e.g. `Presence: presence_source=union, type_confidence>=0.6`. Right column: the two contrasted masks, green = present only in the first (`similarity`, or the default type threshold camera-only), magenta = present only in the second (the selected type-head settings), yellow = present in both, tinted onto the camera (top) and alone on black (bottom). |

A model without a type head (similarity logits only) has no type-head mask to contrast: the contrasted masks are left out
of the `.npz` and the summary (`compared` is `null`), and the video shows only the left column.
