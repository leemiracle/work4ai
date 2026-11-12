## CWIP (Contrastive World-Image Pre-training)

CWIP computes joint representations from paired camera and world images/videos and produces per-patch consistency and object-type predictions. This directory contains the model wrapper, configs, visualization helpers, command‑line tools, and tests.

## Contents

- [Requirements](#requirements)
- [Get model checkpoints](#get-model-checkpoints)
- [Quickstart (Bazel)](#quickstart-bazel)
- [Programmatic usage (Python)](#programmatic-usage-python)
- [Camera-only mode](#camera-only-mode)
- [Bazel targets](#bazel-targets)
- [Run tests](#run-tests)
- [Test coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)
- [See also](#see-also)

### Directory layout

- `cwip.py`: CWIP inference module exposing `CWIPInference` and helpers
- `modules/`: encoder/decoder modules and lazy config defaults
- `visualization/`: image/video preprocessing and visualization utilities
- `tools/`: CLI tools (run inference)
- `tests/`: unit tests and smoke tests

## Requirements

- Bazel/dazel environment set up for this repo
  - See the [main README](../../../../README.md) environment setup section (step 5) for instructions on sourcing `tools/env_setup.sh` to setup the build environment and check host machine requirements
- Git LFS installed (`git lfs install`) so the model weights are materialized on clone/pull
- GPU recommended (CUDA) for real‑time inference; CPU is supported but slower
- Model checkpoint stored in HuggingFace format under `checks/utils/models/cwip/checkpoints/` (`config.json` + `model.safetensors`)

Notes:
- Bazel targets declare Python deps (e.g., `torch`, `einops`, `safetensors`, `detectron2` config, `numpy`, `torchinfo`). If running outside Bazel, ensure these are available.

## Get model checkpoints

The CWIP model weights are stored in-tree via Git LFS at `checks/utils/models/cwip/checkpoints/` (the same pattern
used for the SegFormer model). After cloning the repo, materialize the weights with:

```bash
git lfs pull
```

`model.safetensors` is tracked by Git LFS; `config.json` is a normal git file. The Bazel
`//checks/utils/models/cwip/checkpoints:cwip_model` filegroup exposes both files to consuming targets via runfiles.

## Quickstart (Bazel)

The inference binary (`tools:inference`) has **no subcommands** — it always loads from `--model_path` (HuggingFace layout) and then runs inference. Pass flags only after `--` (do not use a `load` verb; that belongs to other tools such as `convert_cwip_to_hf.py`).

Run a quick dummy forward pass after loading a checkpoint:

```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --test_inference
```

Run on a camera/world video pair and save visualizations:

```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --camera_video_path /path/to/camera.mp4 \
  --world_video_path /path/to/world.mp4 \
  --output_dir $(pwd)/tmp/cwip_output
```

e.g.,

```
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --camera_video_path $(pwd)/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --world_video_path $(pwd)/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_0.mp4 \
  --output_dir $(pwd)/tmp/cwip_output
```

Run only the camera embedding + object-type path (no world encoder / similarity head) with `--camera_only_mode` — only a camera video is needed:

```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --camera_only_mode \
  --camera_video_path $(pwd)/checks/sample_data/0d21d408-ceca-4af6-9c4b-4f6f78ee7459_1727936028200000_rgb.mp4 \
  --output_dir $(pwd)/tmp/cwip_output \
  --image_size 720,1280
```

Note: the two-branch path resizes the camera down to the world frame size, but camera-only has no world frame and otherwise runs at the camera's native resolution (e.g. the 1080×1920 sample), which is memory-heavy. Pass `--image_size H,W` (e.g. `720,1280`) to bound patch-former memory; alternatively lower `--batch_size`.

See [`tools/README.md`](tools/README.md#inferencepy) for the full flag reference and the camera-only visualization subset.

## Programmatic usage (Python)

```python
import torch
from checks.utils.models.cwip.cwip import CWIPInference

# Load from a HuggingFace-format checkpoint directory
model = CWIPInference.from_hf_format(
    model_path="checks/utils/models/cwip/checkpoints",
    device="cuda",  # or "cpu"
)

# Single-frame inference (dummy example)
H, W = model.image_size  # defaults; will auto-adjust to input at runtime
camera = torch.randn(1, 3, H, W).to("cuda")
world = torch.randn(1, 3, H, W).to("cuda")

with torch.no_grad():
    out = model.forward(camera_image=camera, world_image=world)

print(out["camera_features"].shape, out["world_features"].shape)

# Optional: generate visualizations when you also have videos/frames
model.create_inference_visualizations(
    output_batch=out,
    data_batch={"camera_image": camera, "world_image": world},
    output_dir="/tmp/cwip_vis",
    iteration=0,
)
```

API highlights (see `cwip.py` for full signatures):
- `CWIPInference.from_hf_format(model_path, device)`: load model+config from a saved directory
- `CWIPInference.forward(camera_image, world_image=None) -> dict`: returns global and spatial features and optional patch logits under keys:
  - `camera_global_features`, `world_global_features`, `camera_spatial_features`, `world_spatial_features`, `camera_spatial_features_list`, `world_spatial_features_list`, `patch_similarity_logits`, `patch_type_logits`
  - When the model's config has `inference.camera_only_mode=True`, `world_image` may be `None`; the world encoder and similarity head are skipped and the world-derived outputs (`world_global_features`, `world_spatial_features_list`, `patch_similarity_logits`) are `None`.
- `CWIPInference.encode_image(...)`: encode an image through the camera/world path
- `CWIPInference.create_inference_visualizations(...)`: save tiled videos and patch visualizations

## Camera-only mode

Camera-only mode loads the full two-branch checkpoint but skips the world encoder and similarity head at
forward time — zero world FLOPs. Only the camera encoder/aligner, camera global embedding, and
object-type prediction path run. The checkpoint structure is unchanged; `camera_only_mode` is a runtime
flag, not a separate model file.

**Requirement:** the object-type path must be self-attention only (`patch_classifier.cross_attn_frequency=None`
in the saved config). This is true for all `use_separate_necks=True` checkpoints. Attempting camera-only
inference on a cross-attention type neck raises `ValueError` immediately at the first forward call.

### Invocation methods

**1. CLI** (`tools/inference.py`) — pass `--camera_only_mode`; `--world_video_path` is ignored and a
black world tensor is synthesized for visualization tiling only:

```bash
dazel run //checks/utils/models/cwip/tools:inference -- \
  --model_path checks/utils/models/cwip/checkpoints \
  --device cuda \
  --camera_only_mode \
  --camera_video_path /path/to/camera.mp4 \
  --output_dir $(pwd)/tmp/cwip_output \
  --image_size 720,1280   # recommended: native camera res can be memory-heavy without a world frame to resize to
```

See `tools/README.md` for the full flag reference and visualization output subset.

**2. `load_from_hf_format()` helper** — pass `camera_only_mode=True`; the flag is applied after loading so
the full checkpoint (including world weights) is read normally:

```python
from checks.utils.models.cwip.tools.inference import load_from_hf_format

model = load_from_hf_format(
    model_path="checks/utils/models/cwip/checkpoints",
    device="cuda",
    camera_only_mode=True,
)

import torch
camera = torch.randn(1, 3, 720, 1280, device="cuda", dtype=model.precision)
with torch.no_grad():
    out = model.forward(camera_image=camera, world_image=None)

# world_global_features, world_spatial_features_list, patch_similarity_logits are all None
print(out["patch_type_logits"].shape)   # (1, num_type_classes, H/P, W/P)
```

**3. `InferenceConfig` at construction** — set `camera_only_mode=True` directly in the config before
passing to `CWIPInference`. This is the lowest-level entry point and is what the CLI and helper both use
internally:

```python
from checks.utils.models.cwip.cwip import CWIPInference
from checks.utils.models.cwip.modules.configs.defaults.model import InferenceConfig

model = CWIPInference.from_hf_format("checks/utils/models/cwip/checkpoints", device="cuda")
model.config.inference.camera_only_mode = True   # flip after load — equivalent to method 2

# Or set at construction time via a custom ModelConfig:
# config.inference = InferenceConfig(camera_only_mode=True)
# model = CWIPInference(config)
```

### What changes in camera-only mode

| Output key | Two-branch | Camera-only |
|---|---|---|
| `camera_global_features` | Tensor | Tensor |
| `camera_spatial_features_list` | list[Tensor] | list[Tensor] |
| `world_global_features` | Tensor | **None** |
| `world_spatial_features_list` | list[Tensor] | **None** |
| `patch_similarity_logits` | Tensor | **None** |
| `patch_type_logits` | Tensor (if classifier present) | Tensor (if classifier present) |

Visualization output is also reduced — `tiled_video`, `combined_patch_vis`, and `detailed_patch_type_vis`
are written; similarity-branch outputs (`similarity_radial`, `detailed_patch_similarity_vis`,
`class_percentage_radial`, `class_pixel_count_radial`) are not produced. See `tools/README.md` for details.

## Bazel targets

- Library: `//checks/utils/models/cwip:cwip`
- Inference tool: `//checks/utils/models/cwip/tools:inference`
- Checkpoint filegroup: `//checks/utils/models/cwip/checkpoints:cwip_model`
- Tests: `//checks/utils/models/cwip/...`

## Run tests

```bash
dazel test //checks/utils/models/cwip/...
```

The test suite includes CPU-only smoke tests and basic video preprocessing checks using runfiles data declared in the test target.

## Test coverage

To run unit test coverage for the CWIP module:

* Generate unit test coverage data:
    ```bash
    dazel coverage --combined_report=lcov --verbose_failures //checks/utils/models/cwip/... -- -//:requirements.test
    ```
* Generate the HTML report:
    ```bash
    genhtml --no-function-coverage --branch-coverage --output <output_dir> bazel-out/_coverage/_coverage_report.dat
    ```
    * An `index.html` file will be generated within the `<output_dir>` specified to view in a web browser
* Run linters and formatters on the CWIP module:
    ```bash
    dazel fix //checks/utils/models/cwip/...
    ```
    * This will automatically fix linting and formatting violations. Manually fix any violations that remain after running `dazel fix`

## Troubleshooting

- Missing checkpoints: run `git lfs pull` to materialize `model.safetensors`, or verify `--model_path` points to a valid directory containing `config.json` and `.safetensors` files.
- No GPU available:
  - GPU access in dazel is controlled by `.dazelrc` (see main README). By default, `DAZEL_GPUS = "all"` is set, which should expose all GPUs to the Docker container via nvidia-container-toolkit.
  - If GPUs are not accessible in dazel, try these steps in order:
    1. **Restart the dazel container** - The container may have been created before GPU configuration was set. Stop and remove the existing container, then run any dazel command to recreate it:
       ```bash
       docker stop cosmos_eval && docker rm cosmos_eval
       dazel run //checks/utils/models/cwip/tools:inference -- --model_path checks/utils/models/cwip/checkpoints --device cuda --test_inference
       ```
    2. Verify NVIDIA drivers are installed on the host (`nvidia-smi` should work)
    3. Verify NVIDIA Container Toolkit is installed and Docker is configured to use it (see main README, step 5)
       - Check with: `docker info | grep -i runtime` (should show `nvidia` runtime)
    4. Test GPU access in the dazel container - run: `dazel run //checks/utils/models/cwip/tools:inference -- --model_path checks/utils/models/cwip/checkpoints --device cuda --test_inference`
       - If you see "RuntimeError: No CUDA GPUs are available", the container may not have CUDA libraries or the nvidia runtime may not be properly invoked
    5. If `DAZEL_GPUS` is overridden in `user.dazelrc`, ensure it's set to `"all"` or a valid GPU specification
    6. Note: `DAZEL_GPUS = "all"` is set by default in `.dazelrc` (line 143), which should automatically invoke nvidia-container-toolkit runtime. However, if GPUs are still not accessible after restarting the container, the dazel Docker image may need to be rebuilt with CUDA support, or there may be an issue with the nvidia-container-toolkit configuration.
  - If GPU access is not working, set `--device cpu` (performance will be lower).
- Video decoding goes through `checks/utils/video.py`, which shells out to `ffmpeg`/`ffprobe`. Under Bazel these resolve to the vendored LGPL build; when running outside Bazel, put *that* build on `PATH` rather than a host install. The codec ladder and its tests assume the vendored allow-list (see `third_party/ffmpeg/tar.sh`), and a distro ffmpeg carries a different codec set, so it can fail or silently pick another decoder.
- Git LFS pointer instead of weights: if `model.safetensors` is only a small text pointer file, run `git lfs install` then `git lfs pull` to fetch the actual weights.

### Prerequisites

- A trained CWIP checkpoint converted to HuggingFace format (`config.json` + `model.safetensors`).
- Git LFS installed (`git lfs install`).

### Steps

1. Replace the files in place:
   ```bash
   cp /path/to/new/config.json        checks/utils/models/cwip/checkpoints/config.json
   cp /path/to/new/model.safetensors  checks/utils/models/cwip/checkpoints/model.safetensors
   ```
   `model.safetensors` is already tracked by Git LFS via `.gitattributes`
   (`checks/utils/models/cwip/checkpoints/model.safetensors filter=lfs ...`), so `git add` will store it as an LFS
   object automatically.
2. Stage and verify the LFS pointer:
   ```bash
   git add checks/utils/models/cwip/checkpoints/config.json checks/utils/models/cwip/checkpoints/model.safetensors
   git lfs ls-files | grep cwip   # confirm model.safetensors is tracked by LFS
   ```
3. Commit and push as usual. Reviewers and automated builds fetch the new weights via `git lfs pull`.
4. Verify the inference target loads the new weights:
   ```bash
   dazel run //checks/utils/models/cwip/tools:inference -- --device cuda --test_inference
   ```

## See also

- [`docs/checks/objects.md`](../../../../docs/checks/objects.md) for how CWIP is used as the static processor in the Objects check
- [`checks/utils/models/cwip/tools/README.md`](tools/README.md) for CLI usage
- [`checks/utils/models/cwip/BUILD`](BUILD) for dependency declarations
