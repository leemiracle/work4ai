<!-- source: DeepWiki mcp.deepwiki.com · repo opencv/opencv · page 17 Photo and Computational Photography · fetched 2026-10-30 -->

# Photo and Computational Photography

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [modules/photo/include/opencv2/photo.hpp](modules/photo/include/opencv2/photo.hpp)
- [modules/photo/src/align.cpp](modules/photo/src/align.cpp)
- [modules/photo/src/calibrate.cpp](modules/photo/src/calibrate.cpp)
- [modules/photo/src/hdr_common.cpp](modules/photo/src/hdr_common.cpp)
- [modules/photo/src/hdr_common.hpp](modules/photo/src/hdr_common.hpp)
- [modules/photo/src/merge.cpp](modules/photo/src/merge.cpp)
- [modules/photo/src/tonemap.cpp](modules/photo/src/tonemap.cpp)
- [modules/photo/test/test_hdr.cpp](modules/photo/test/test_hdr.cpp)

</details>



The `opencv_photo` module provides advanced algorithms for image restoration, enhancement, and computational photography tasks that extend beyond standard pixel-level filtering. It covers high dynamic range (HDR) imaging, non-local means denoising, geometric inpainting, Poisson-based seamless cloning, contrast-preserving decolorization, non-photorealistic rendering, color correction models, and interactive segmentation tools.

This page serves as a high-level parent overview of `modules/photo/`. For detailed technical explorations of individual subsystems, refer to the child pages:
- For HDR pipeline details, exposure alignment, and tonemapping operators, see [HDR Imaging and Tone Mapping](#17.1).
- For denoising invokers, inpainting methods, and Poisson blending solvers, see [Denoising, Inpainting, and Seamless Cloning](#17.2).
- For color correction models and interactive segmentation, see [Color Correction and Intelligent Scissors](#17.3).

---

## High-Level Module Overview and Architecture

All public classes and functions for computational photography are declared in [modules/photo/include/opencv2/photo.hpp](). The module depends directly on `opencv_core` for foundational matrix containers (`Mat`, `UMat`) and `opencv_imgproc` for basic filtering and color space transformations.

**Module Entity Mapping Diagram:**

```mermaid
graph TD
    subgraph "Natural Language Space"
        ["Inpainting"]
        ["Denoising"]
        ["HDR & Tonemapping"]
        ["Seamless Cloning"]
        ["Color Correction"]
    end

    subgraph "Code Entity Space"
        ["cv::inpaint"]
        ["cv::fastNlMeansDenoising"]
        ["cv::Tonemap", "cv::AlignMTB", "cv::MergeDebevec"]
        ["cv::seamlessClone", "cv::Cloning"]
        ["cv::ccm::ColorCorrectionModel"]
    end

    ["Inpainting"] --> ["cv::inpaint"]
    ["Denoising"] --> ["cv::fastNlMeansDenoising"]
    ["HDR & Tonemapping"] --> ["cv::Tonemap"]
    ["HDR & Tonemapping"] --> ["cv::AlignMTB"]
    ["Seamless Cloning"] --> ["cv::seamlessClone"]
    ["Color Correction"] --> ["cv::ccm::ColorCorrectionModel"]
```

Sources: [modules/photo/include/opencv2/photo.hpp:43-82]()

---

## HDR Imaging and Tone Mapping

The HDR subsystem enables the reconstruction and display of high dynamic range scenes from multiple low dynamic range (LDR) exposures. The pipeline consists of three primary stages: exposure alignment (`AlignMTB`), camera response function calibration (`CalibrateCRF`), and exposure merging (`MergeExposures`), followed by tone mapping operators (`Tonemap`) to map floating-point HDR images back to displayable ranges.

For complete details on alignment algorithms, CRF optimization equations, and tone mapping operators (Drago, Reinhard, Mantiuk, Durand), see [HDR Imaging and Tone Mapping](#17.1).

Sources: [modules/photo/include/opencv2/photo.hpp:57-60](), [modules/photo/src/tonemap.cpp:56-106](), [modules/photo/test/test_hdr.cpp:88-120]()

---

## Denoising, Inpainting, and Seamless Cloning

This domain encompasses spatial and temporal restoration tools. Image denoising is powered by the Non-Local Means (NLM) algorithm implemented via `fastNlMeansDenoising` and parallel CPU invokers or OpenCL kernels. Inpainting restores corrupted regions using Navier-Stokes (`INPAINT_NS`) or Fast Marching (`INPAINT_TELEA`) techniques. Seamless cloning leverages 2D Discrete Sine Transforms to solve Poisson equations for natural object compositing (`seamlessClone`), alongside contrast-preserving decolorization (`decolor`) and non-photorealistic rendering filters.

For detailed documentation on NLM patch weighting, Poisson solvers, and rendering filters, see [Denoising, Inpainting, and Seamless Cloning](#17.2).

Sources: [modules/photo/include/opencv2/photo.hpp:90-149](), [modules/photo/src/denoising.cpp:48-102]()

---

## Color Correction and Intelligent Scissors

The module also houses specialized color calibration models and interactive segmentation helpers. The color correction machinery (`photo/src/ccm`) handles polynomial color correction, linearization, and illuminant adjustments. Additionally, interactive segmentation tools such as Intelligent Scissors provide graph-based boundary extraction for image editing workflows.

For architecture details on color spaces, illuminant models, and interactive segmentation tests, see [Color Correction and Intelligent Scissors](#17.3).

Sources: [modules/photo/include/opencv2/photo.hpp:48-48]()

---

