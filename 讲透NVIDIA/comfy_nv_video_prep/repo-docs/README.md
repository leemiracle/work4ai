# ComfyUI_VideoPrep

NVIDIA Video Preparation nodes for ComfyUI — a suite of interactive tools for cropping, mask editing, segmentation, keyframe animation, and multi-layer compositing, designed for video generation pre-production workflows.

# Overview

ComfyUI_VideoPrep provides 5 custom nodes that keep the entire video preparation stage inside ComfyUI. Artists can interactively crop, segment, edit masks, and keyframe-animate layers without leaving the canvas, then pipe results directly into downstream generation nodes (Wan, LTX, etc.).

**Nodes included:**

| Node | Description |
|------|-------------|
| **VideoPrep Interactive Crop** | Draggable crop rectangle with live preview; simultaneous image + mask cropping |
| **VideoPrep Preview Bridge** | Image/mask pass-through with premultiplied alpha and multiple output modes |
| **VideoPrep Preview Bridge (Advanced)** | Built-in persistent mask editor with brush/erase and Cut/Keep/Extend modes |
| **VideoPrep TTM Interactive Editor** | Click-to-segment with SAM2, polygon editing, multi-layer keyframe animation |
| **VideoPrep TTM Compose & Animate** | Multi-layer compositor with up to 4 subjects, background pan/zoom/rotate |

# Getting Started

```bash
# Clone the repository
git clone ssh://git@gitlab-master.nvidia.com:12051/awd/alt_comfyui_ttm_nodes.git

# Copy to ComfyUI custom_nodes
cp -r alt_comfyui_ttm_nodes /path/to/ComfyUI/custom_nodes/ComfyUI_VideoPrep

# Install dependencies
pip install -r /path/to/ComfyUI/custom_nodes/ComfyUI_VideoPrep/requirements.txt

# Restart ComfyUI — VideoPrep nodes will appear in the node menu
```

# Requirements

- **OS:** Windows 10/11, Linux (Ubuntu 20.04+)
- **Runtime:** Python 3.10+, ComfyUI (latest stable)
- **GPU:** NVIDIA GPU with CUDA support
- **VRAM (Minimum):** 4 GB
- **VRAM (Recommended):** 8 GB+ (for SAM2 segmentation features)

### Python Dependencies

- `numpy`
- `opencv-python`
- `imageio`, `imageio-ffmpeg`

### Optional Dependencies

- **[comfyui-sam2](https://github.com/neverbiasu/comfyui-sam2)** — for click-to-segment in the Interactive Editor. Install via ComfyUI Manager. SAM2 models auto-download on first use.

# Usage

Load one of the example workflows from the `workflows/` directory:

- `example_basic.json` — Basic interactive editor usage
- `example_compose_animate.json` — Multi-layer composition and animation
- `example_with_wan.json` — Integration with Wan video generation pipeline

### Node Details

<details>
<summary><b>VideoPrep Interactive Crop</b></summary>

- Click and drag to draw a crop region directly on the image
- Resize by dragging corners/edges; move by dragging inside
- Double-click to reset; grid snapping for latent alignment
- **Inputs:** `image`, `mask` (optional), `crop_data`, `snap_to_grid`
- **Outputs:** `cropped_image`, `cropped_mask`, `x`, `y`, `width`, `height`

</details>

<details>
<summary><b>VideoPrep Preview Bridge</b></summary>

- Handles both images and masks reliably across workflow runs
- Output modes: `original`, `premultiplied`, `cutout_black`, `cutout_white`
- Preview modes: `cutout`, `overlay`, `mask_only`
- **Inputs:** `image`, `mask` (optional), `output_mode`, `preview_mode`
- **Outputs:** `image`, `mask`, `width`, `height`

</details>

<details>
<summary><b>VideoPrep Preview Bridge (Advanced)</b></summary>

- Draw/erase masks directly on the image preview
- Mask stored inside the workflow file — persists across runs, saves, and restarts
- Multiple mask modes: Cut, Keep, Extend
- Auto-imports existing alpha channels from input images
- **Inputs:** `image`, `mask` (optional), `output_mode`, `mask_combine`, `mask_data`
- **Outputs:** `image`, `mask`, `preview`, `width`, `height`

</details>

<details>
<summary><b>VideoPrep TTM Compose & Animate</b></summary>

- Up to 4 animated subjects over an animated background
- Per-layer keyframe transforms: position, rotation, scale
- Background animation: pan, zoom, rotate with independent keyframe track
- Timeline scrubber for animation preview
- **Inputs:** `background`, up to 4× (`subject_N`, `mask_N`), `editor_data`, `total_frames`
- **Outputs:** `frames`, `width`, `height`

</details>

<details>
<summary><b>VideoPrep TTM Interactive Editor</b></summary>

- Click-to-segment using SAM2 (optional) for detailed mask creation
- Include/exclude points for precise segmentation control
- Manual polygon drawing fallback (if SAM2 is not installed)
- Multi-layer keyframe animation: position, rotation, scale, hue
- Animation timeline preview slider
- **Inputs:** `image`, `editor_data`, `total_frames`
- **Outputs:** `frames`, `masks`, `width`, `height`

</details>

## Releases & Roadmap

- Releases / Changelog: [CHANGELOG.md](CHANGELOG.md)

# Contribution Guidelines

**This project is currently not accepting any contributions.**

All source code is original NVIDIA-authored work. No third-party code is included.

- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Contributing policy: [CONTRIBUTING.md](CONTRIBUTING.md)

## Governance & Maintainers

- Governance: [GOVERNANCE.md](GOVERNANCE.md)
- Maintainers: NVIDIA AWD Team — see [MAINTAINERS.md](MAINTAINERS.md)

## Security

- Vulnerability disclosure: [SECURITY.md](SECURITY.md)
- **Do not file public issues for security reports.** Report to [psirt@nvidia.com](mailto:psirt@nvidia.com).

## Support

- Level: **Experimental**
- How to get help: File an issue
- Details: [SUPPORT.md](SUPPORT.md)

# License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
