<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DeepStream · page 4 Sample & Reference Applications · fetched 2026-10-26 -->

# Sample & Reference Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [includes/nvdsinferserver_common.proto](includes/nvdsinferserver_common.proto)
- [scripts/print_env.sh](scripts/print_env.sh)
- [src/README.md](src/README.md)
- [src/apps/reference_apps/README.md](src/apps/reference_apps/README.md)
- [src/apps/sample_apps/README.md](src/apps/sample_apps/README.md)
- [src/apps/sample_apps/deepstream-appsrc-test/README](src/apps/sample_apps/deepstream-appsrc-test/README)
- [src/apps/sample_apps/deepstream-infer-tensor-meta-test/README](src/apps/sample_apps/deepstream-infer-tensor-meta-test/README)
- [src/apps/sample_apps/deepstream-multigpu-nvlink-test/README](src/apps/sample_apps/deepstream-multigpu-nvlink-test/README)
- [src/apps/sample_apps/deepstream-nvdsanalytics-test/README](src/apps/sample_apps/deepstream-nvdsanalytics-test/README)
- [src/apps/sample_apps/deepstream-opencv-test/README](src/apps/sample_apps/deepstream-opencv-test/README)
- [src/apps/sample_apps/deepstream-preprocess-test/README](src/apps/sample_apps/deepstream-preprocess-test/README)
- [src/apps/sample_apps/deepstream-test5/README](src/apps/sample_apps/deepstream-test5/README)
- [src/apps/sample_apps/deepstream-user-metadata-test/README](src/apps/sample_apps/deepstream-user-metadata-test/README)
- [src/apps/tao_apps/README.md](src/apps/tao_apps/README.md)
- [src/apps/tao_apps/apps/tao_others/deepstream-mdx-perception-app/README.md](src/apps/tao_apps/apps/tao_others/deepstream-mdx-perception-app/README.md)
- [src/apps/tao_apps/apps/tao_others/deepstream-nvocdr-app/README.md](src/apps/tao_apps/apps/tao_others/deepstream-nvocdr-app/README.md)
- [src/apps/tao_apps/configs/app/config_nvdsanalytics.txt](src/apps/tao_apps/configs/app/config_nvdsanalytics.txt)
- [src/gst-plugins/README.md](src/gst-plugins/README.md)
- [src/utils/README.md](src/utils/README.md)

</details>



This section provides a high-level overview of the sample and reference applications included in the DeepStream SDK 9.1. These applications serve as the primary entry points for developers to understand pipeline construction, metadata handling, and the integration of advanced AI models.

DeepStream applications are broadly categorized into core tutorials for foundational learning, specialized reference apps for advanced use cases (such as 3D sensing and IPC), and TAO-specific applications for deploying pre-trained NVIDIA models.

### Application Categories Overview

The codebase organizes applications based on their complexity and target technology stack:

| Category | Location | Purpose |
|---|---|---|
| **Core Tutorial Apps** | `src/apps/sample_apps/` | Foundational GStreamer-based pipelines (Test1-Test5). |
| **Triton Sample Apps** | `src/apps/sample_apps/` | Applications leveraging `nvinferserver` for multi-framework inference. |
| **TAO Model Apps** | `src/apps/tao_apps/` | Integration of TAO Toolkit models (e.g., PeopleNet, BodyPose3D). |
| **Advanced Reference Apps** | `src/apps/reference_apps/` | Complex features like 3D tracking, VLM integration, and Anomaly Detection. |

**Sources:** [src/README.md:28-52](), [src/apps/sample_apps/README.md:47-128]()

---

### Core Tutorial Sample Apps

The core tutorial applications provide a progressive learning path, starting from a simple single-stream detector to a production-grade multi-stream application with cloud connectivity.

*   **Test 1-3:** Covers basic decoding, primary inference (`nvinfer`), secondary classification, and multi-stream handling via `uridecodebin` [src/apps/sample_apps/README.md:51-56]().
*   **Test 4-5:** Introduces cloud messaging via `nvmsgbroker` (Kafka/MQTT) and advanced configurations including RTSP output [src/apps/sample_apps/README.md:57-58]().
*   **Metadata & Analytics:** Specialized tests for accessing raw tensor metadata (`deepstream-infer-tensor-meta-test`) and spatial analytics (`deepstream-nvdsanalytics-test`) [src/apps/sample_apps/README.md:64-87]().

For implementation details and configuration patterns, see **[Core Tutorial Sample Apps](#4.1)**.

**Sources:** [src/apps/sample_apps/README.md:49-59](), [src/apps/sample_apps/deepstream-infer-tensor-meta-test/README:59-64]()

---

### Triton Inference Server Sample Apps

These applications demonstrate how to use the `gst-nvinferserver` plugin to perform inference using the NVIDIA Triton Inference Server. This allows for the use of models from multiple frameworks (TensorRT, ONNX, TensorFlow, PyTorch) within a DeepStream pipeline.

*   **TritonOnnxYolo:** Demonstrates a custom library (`libnvdstriton_custom_impl_yolo.so`) for parsing dynamic-sized output tensors from ONNX YOLOv3 models [src/apps/sample_apps/README.md:127]().
*   **TritonBackendEnsemble:** Shows a custom Triton C++ backend that interacts with DeepStream stream IDs for ensemble model execution [src/apps/sample_apps/README.md:126]().

For details on Triton container setup and gRPC vs C-API modes, see **[Triton Inference Server Sample Apps](#4.2)**.

**Sources:** [src/apps/sample_apps/README.md:117-128](), [src/apps/sample_apps/deepstream-infer-tensor-meta-test/README:46-54]()

---

### TAO Toolkit Model Apps

The TAO applications are optimized for deploying high-accuracy pre-trained models from the NVIDIA TAO Toolkit. These apps include specialized post-processing for various model architectures.

*   **Detection & Segmentation:** Support for `PeopleNet Transformer`, `CitySemSegFormer`, and `Mask2Former` [src/apps/tao_apps/README.md:52]().
*   **Specialized Perception:** Includes `BodyPose3DNet`, `OCRNet` for text recognition, and `ReIdentificationNet` for person/retail item re-identification [src/apps/tao_apps/README.md:35-42]().

For model download scripts and `nvinfer` configuration files, see **[TAO Toolkit Model Apps](#4.3)**.

**Sources:** [src/apps/tao_apps/README.md:18-57](), [src/apps/tao_apps/apps/tao_others/deepstream-mdx-perception-app/README.md:19-35]()

---

### Advanced Reference Applications

Reference applications demonstrate complex system-level features and cutting-edge AI integrations that go beyond standard object detection.

*   **3D Tracking:** Single-view and multi-view 3D tracking for human model reconstruction and calibrated camera networks [src/apps/reference_apps/README.md:36-40]().
*   **MaskTracker:** Multi-object tracking and segmentation using the Segment Anything Model 2 (SAM2) [src/apps/reference_apps/README.md:33-35]().
*   **VLM Integration:** A dedicated plugin for Vision-Language Models (VLM) using `vLLM` for real-time video understanding [src/apps/reference_apps/README.md:52-53]().
*   **System Utilities:** Runtime source addition/deletion and IPC-based buffer sharing between independent pipelines [src/apps/reference_apps/README.md:31-32](), [src/apps/reference_apps/README.md:48-49]().

For architecture diagrams and advanced configuration, see **[Advanced Reference Applications](#4.4)**.

**Sources:** [src/apps/reference_apps/README.md:28-53]()

---

### Application to Code Mapping

The following diagrams illustrate the relationship between the high-level application categories and the underlying code entities in the SDK.

#### Mapping: Core and Reference App Structure
```mermaid
graph TD
    subgraph "Application Layer"
        [deepstream-app] --> |"Uses"| [libnvdsgst_helper.so]
        [deepstream-test5] --> |"Uses"| [nvmsgbroker]
        [deepstream-masktracker] --> |"Uses"| [nvmultiobjecttracker]
    end

    subgraph "Code Entity Space"
        [libnvdsgst_helper.so] --- [src/utils/nvstreammux/]()
        [nvmsgbroker] --- [src/utils/nvmsgbroker/]()
        [nvmultiobjecttracker] --- [src/utils/nvmultiobjecttracker/]()
    end
```
**Sources:** [src/utils/README.md:40-52](), [src/apps/sample_apps/README.md:53-58](), [src/apps/reference_apps/README.md:33-35]()

#### Mapping: TAO and Triton Integration
```mermaid
graph LR
    subgraph "TAO Apps"
        [ds-tao-detection] --> |"Configures"| [nvinfer]
        [ds-tao-segmentation] --> |"Parses"| [nvdsinfer_custombboxparser_tao.cpp]
    end

    subgraph "Triton Samples"
        [TritonOnnxYolo] --> |"Implements"| [libnvdstriton_custom_impl_yolo.so]
        [TritonBackendEnsemble] --> |"Implements"| [libnvdstriton_custom_impl_ensemble.so]
    end

    subgraph "Inference Libraries"
        [nvinfer] --- [src/utils/nvdsinfer/]()
        [nvinferserver] --- [src/utils/nvdsinferserver/]()
    end
```
**Sources:** [src/apps/tao_apps/README.md:52-57](), [src/apps/sample_apps/README.md:117-128](), [src/utils/README.md:30-35]()

---

