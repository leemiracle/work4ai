<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/3DObjectReconstruction · page 8 Troubleshooting · fetched 2026-10-26 -->

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report_form.yml](.github/ISSUE_TEMPLATE/bug_report_form.yml)
- [print_env.sh](print_env.sh)

</details>



This document provides systematic approaches to diagnosing and resolving common issues encountered when using the NVIDIA 3D Object Reconstruction system. It covers problems ranging from installation failures to runtime pipeline errors and performance bottlenecks.

For installation guidance, see [Installation & Deployment](#2.1). For configuration details, see [Configuration Management](#5). For API reference during debugging, see [API Reference](#6).

## Quick Diagnostics

The system provides automated environment diagnostics through the `print_env.sh` script, which is referenced in the bug report template for comprehensive environment analysis.

### Environment Information Collection

Run the diagnostic script to gather system information:

```bash
./print_env.sh > environment_report.txt
```

This script collects critical information including GPU status, Docker configuration, CUDA toolkit versions, and Python environment details as shown in [print_env.sh:1-107]().

**Key Environment Checks:**
| Component | Check Command | Expected Output |
|-----------|---------------|-----------------|
| GPU Driver | `nvidia-smi` | CUDA-compatible driver |
| Docker | `docker --version` | Version 20.10+ recommended |
| NVIDIA Container Toolkit | `nvidia-container-toolkit --version` | Required for GPU access |
| CUDA Compiler | `nvcc --version` | CUDA 11.8+ |
| Python | `python --version` | Python 3.8+ |

Sources: [print_env.sh:25-61]()

## Installation & Deployment Issues

### Docker Container Problems

```mermaid
flowchart TD
    DEPLOY_START["deploy.sh execution"] --> DOCKER_CHECK{"Docker available?"}
    DOCKER_CHECK -->|No| INSTALL_DOCKER["Install Docker Engine"]
    DOCKER_CHECK -->|Yes| COMPOSE_CHECK{"Docker Compose available?"}
    
    COMPOSE_CHECK -->|No| INSTALL_COMPOSE["Install Docker Compose"]
    COMPOSE_CHECK -->|Yes| GPU_CHECK{"NVIDIA Container Toolkit?"}
    
    GPU_CHECK -->|No| INSTALL_NVIDIA_DOCKER["Install NVIDIA Container Toolkit"]
    GPU_CHECK -->|Yes| BUILD_IMAGES["Build container images"]
    
    BUILD_IMAGES --> BUILD_SUCCESS{"Build successful?"}
    BUILD_SUCCESS -->|No| CHECK_DOCKERFILE["Check Dockerfile syntax"]
    BUILD_SUCCESS -->|Yes| START_SERVICES["Start services"]
    
    START_SERVICES --> SERVICE_CHECK{"Services healthy?"}
    SERVICE_CHECK -->|No| CHECK_LOGS["Check container logs"]
    SERVICE_CHECK -->|Yes| DEPLOYMENT_COMPLETE["Deployment Complete"]
    
    INSTALL_DOCKER --> DOCKER_CHECK
    INSTALL_COMPOSE --> COMPOSE_CHECK
    INSTALL_NVIDIA_DOCKER --> GPU_CHECK
    CHECK_DOCKERFILE --> BUILD_IMAGES
    CHECK_LOGS --> TROUBLESHOOT_RUNTIME["Runtime troubleshooting"]
```

**Common Docker Issues:**

| Problem | Symptoms | Solution |
|---------|----------|----------|
| GPU not accessible | `RuntimeError: No CUDA devices found` | Verify NVIDIA Container Toolkit installation |
| Out of memory during build | Docker build fails with OOM | Increase Docker memory limits |
| Port conflicts | `Port already in use` | Check for conflicting services on ports 8888, 8000 |
| Permission denied | `Permission denied writing to /var/run/docker.sock` | Add user to docker group |

Sources: [print_env.sh:33-48]()

### Model Download Failures

The system requires several pre-trained models. Download failures typically occur during first-time setup:

```bash
# Check model availability
ls -la ~/.cache/torch/hub/checkpoints/
ls -la ~/.cache/objectreconstruction/
```

**Model Dependencies:**
- FoundationStereo weights
- SAM2 checkpoints
- RoMa feature matching models
- BundleSDF neural network weights

Sources: Based on system architecture diagrams

## Runtime Pipeline Errors

### Component Failure Analysis

```mermaid
graph TD
    INPUT_DATA["Stereo Input Data"] --> FS_PROC["FoundationStereoProcessor"]
    INPUT_DATA --> SAM2_PROC["Sam2Infer"]
    INPUT_DATA --> ROMA_PROC["FeatureMatchingInfer"]
    
    FS_PROC --> FS_ERROR{"FoundationStereo Error?"}
    SAM2_PROC --> SAM2_ERROR{"SAM2 Error?"}
    ROMA_PROC --> ROMA_ERROR{"RoMa Error?"}
    
    FS_ERROR -->|Yes| DEPTH_FAILURE["Depth estimation fails"]
    SAM2_ERROR -->|Yes| SEGMENTATION_FAILURE["Segmentation fails"]
    ROMA_ERROR -->|Yes| MATCHING_FAILURE["Feature matching fails"]
    
    FS_ERROR -->|No| BUNDLE_TRACK["BundleTrack processing"]
    SAM2_ERROR -->|No| BUNDLE_TRACK
    ROMA_ERROR -->|No| BUNDLE_TRACK
    
    BUNDLE_TRACK --> TRACK_ERROR{"Tracking Error?"}
    TRACK_ERROR -->|Yes| POSE_FAILURE["Camera pose estimation fails"]
    TRACK_ERROR -->|No| NERF_TRAIN["NeRF training"]
    
    NERF_TRAIN --> NERF_ERROR{"NeRF Error?"}
    NERF_ERROR -->|Yes| SDF_FAILURE["Neural SDF training fails"]
    NERF_ERROR -->|No| TEXTURE_BAKE["Texture baking"]
    
    DEPTH_FAILURE --> DEBUG_FS["Debug FoundationStereo config"]
    SEGMENTATION_FAILURE --> DEBUG_SAM2["Debug SAM2 bbox/config"]
    MATCHING_FAILURE --> DEBUG_ROMA["Debug RoMa parameters"]
    POSE_FAILURE --> DEBUG_BUNDLE["Debug BundleTrack settings"]
    SDF_FAILURE --> DEBUG_NERF["Debug NeRF architecture"]
```

### NVBundleSDF Framework Errors

The `NVBundleSDF` class in [src/nvidia/objectreconstruction/networks/nvbundlesdf.py]() orchestrates the entire pipeline. Common failure points:

**Pipeline Stage Failures:**
| Stage | Class/Function | Common Error | Debug Approach |
|-------|----------------|--------------|----------------|
| Depth Estimation | `FoundationStereoProcessor` | CUDA OOM | Reduce `depth_scale` parameter |
| Segmentation | `Sam2Infer` | Invalid bounding box | Verify bbox coordinates |
| Feature Matching | `FeatureMatchingInfer` | No correspondences found | Check image overlap |
| Pose Tracking | `NerfRunner.bundle_track()` | Tracking failure | Increase `num_iterations` |
| Neural SDF | `NerfRunner.train()` | Training divergence | Adjust learning rate |

Sources: System architecture and pipeline diagrams

### Data Loading Pipeline Issues

The `ReconstructionDataLoader` handles multi-scale data processing. Common issues:

```mermaid
flowchart LR
    RAW_DATA["Raw Stereo Data"] --> DATA_STRUCTURE{"Correct structure?"}
    DATA_STRUCTURE -->|No| STRUCTURE_ERROR["Missing left/, right/, or metadata"]
    DATA_STRUCTURE -->|Yes| DATALOADER["ReconstructionDataLoader"]
    
    DATALOADER --> TRACK_SCALE["track_dataset scale"]
    DATALOADER --> NERF_SCALE["nerf_dataset scale"]
    DATALOADER --> TEXTURE_SCALE["texture_dataset scale"]
    
    TRACK_SCALE --> TRACK_ERROR{"Loading error?"}
    NERF_SCALE --> NERF_LOAD_ERROR{"Loading error?"}
    TEXTURE_SCALE --> TEXTURE_ERROR{"Loading error?"}
    
    TRACK_ERROR -->|Yes| RESOLUTION_ISSUE["Resolution mismatch"]
    NERF_LOAD_ERROR -->|Yes| MEMORY_ISSUE["Insufficient memory"]
    TEXTURE_ERROR -->|Yes| FORMAT_ISSUE["Unsupported format"]
    
    TRACK_ERROR -->|No| PROCESSING["Pipeline Processing"]
    NERF_LOAD_ERROR -->|No| PROCESSING
    TEXTURE_ERROR -->|No| PROCESSING
```

**Data Structure Requirements:**
```
dataset/
├── left/           # Left camera images
├── right/          # Right camera images
├── depth/          # Optional depth maps
├── masks/          # Optional segmentation masks
└── poses/          # Optional camera poses
```

Sources: Based on data processing system architecture

## Configuration Problems

### Schema Validation Errors

The configuration system uses hierarchical schemas defined in [src/nvidia/objectreconstruction/configs/schema.py](). Validation failures typically indicate:

**Common Configuration Issues:**
| Config Class | Parameter | Issue | Fix |
|-------------|-----------|--------|-----|
| `CameraConfig` | `baseline` | Incorrect stereo baseline | Measure actual camera separation |
| `FoundationStereoConfig` | `model_path` | Model not found | Verify download and path |
| `SAM2Config` | `bounding_box` | Out of bounds | Ensure bbox within image dimensions |
| `BundleTrackConfig` | `num_iterations` | Too low for convergence | Increase to 100-200 |
| `NeRFConfig` | `hidden_dim` | CUDA OOM | Reduce network size |

### Component Configuration Debugging

```mermaid
graph TB
    BASE_CONFIG["base.yaml"] --> CONFIG_PARSER["Configuration Parser"]
    CONFIG_PARSER --> VALIDATION{"Schema Validation"}
    
    VALIDATION -->|Pass| COMPONENT_INIT["Component Initialization"]
    VALIDATION -->|Fail| CONFIG_ERROR["Configuration Error"]
    
    CONFIG_ERROR --> MISSING_PARAM["Missing required parameter"]
    CONFIG_ERROR --> TYPE_MISMATCH["Type mismatch"]
    CONFIG_ERROR --> VALUE_ERROR["Invalid value range"]
    
    COMPONENT_INIT --> FS_CONFIG["FoundationStereoConfig"]
    COMPONENT_INIT --> SAM2_CONFIG["SAM2Config"]
    COMPONENT_INIT --> ROMA_CONFIG["RoMaConfig"]
    COMPONENT_INIT --> BUNDLE_CONFIG["BundleTrackConfig"]
    COMPONENT_INIT --> NERF_CONFIG["NeRFConfig"]
    
    FS_CONFIG --> FS_VALIDATE{"FoundationStereo validation"}
    SAM2_CONFIG --> SAM2_VALIDATE{"SAM2 validation"}
    ROMA_CONFIG --> ROMA_VALIDATE{"RoMa validation"}
    BUNDLE_CONFIG --> BUNDLE_VALIDATE{"BundleTrack validation"}
    NERF_CONFIG --> NERF_VALIDATE{"NeRF validation"}
    
    FS_VALIDATE -->|Fail| MODEL_PATH_ERROR["Model path error"]
    SAM2_VALIDATE -->|Fail| BBOX_ERROR["Bounding box error"]
    ROMA_VALIDATE -->|Fail| FEATURE_ERROR["Feature config error"]
    BUNDLE_VALIDATE -->|Fail| TRACKING_ERROR["Tracking config error"]
    NERF_VALIDATE -->|Fail| NETWORK_ERROR["Network config error"]
```

Sources: Configuration management system architecture

## Environment & Dependency Issues

### CUDA and GPU Problems

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `CUDA out of memory` | Insufficient GPU memory | Reduce batch size or model resolution |
| `No CUDA devices found` | Driver/toolkit mismatch | Update NVIDIA drivers |
| `CUDA runtime error` | Version incompatibility | Check CUDA version compatibility |
| `cuDNN error` | Missing or wrong cuDNN | Install correct cuDNN for CUDA version |

### Python Environment Issues

**Package Conflicts:**
```bash
# Check for conflicting packages
pip check
conda list --show-channel-urls

# Common conflict resolution
pip install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Sources: [print_env.sh:63-98]()

## Performance & Resource Issues

### Memory Management

The pipeline processes high-resolution stereo imagery and maintains neural networks in GPU memory:

**Memory Optimization Strategies:**
| Component | Memory Usage | Optimization |
|-----------|--------------|--------------|
| FoundationStereo | ~4GB GPU | Reduce `depth_scale` |
| SAM2 | ~2GB GPU | Use smaller model variant |
| NeRF Training | ~6GB GPU | Reduce `hidden_dim`, `num_layers` |
| Texture Baking | ~8GB GPU | Lower output resolution |

### Processing Time Issues

**Performance Bottlenecks:**
- Large image resolution in track dataset scale
- High iteration count in bundle tracking
- Complex NeRF architecture
- Dense texture baking resolution

Sources: Performance considerations from system architecture

## Debugging Tools and Techniques

### Logging and Diagnostics

Enable detailed logging for component-specific debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Environment Reporting

Use the automated diagnostic collection as referenced in the bug report template:

```bash
# Generate comprehensive environment report
./print_env.sh > debug_environment.txt

# Include in bug reports per template requirements
```

The bug report template in [.github/ISSUE_TEMPLATE/bug_report_form.yml:70-75]() specifically requests this environment information for effective troubleshooting.

### Component Isolation Testing

Test individual pipeline components to isolate failures:

```python
# Test FoundationStereo in isolation
from src.nvidia.objectreconstruction.networks.nvbundlesdf import FoundationStereoProcessor

# Test SAM2 segmentation
from src.nvidia.objectreconstruction.networks.nvbundlesdf import Sam2Infer

# Test feature matching
from src.nvidia.objectreconstruction.networks.nvbundlesdf import FeatureMatchingInfer
```

Sources: [.github/ISSUE_TEMPLATE/bug_report_form.yml:1-99](), [print_env.sh:1-107]()