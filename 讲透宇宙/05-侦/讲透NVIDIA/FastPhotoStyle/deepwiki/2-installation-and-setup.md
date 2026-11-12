<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/FastPhotoStyle · page 2 Installation and Setup · fetched 2026-10-26 -->

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [TUTORIAL.md](TUTORIAL.md)
- [demo_with_segmentation.gif](demo_with_segmentation.gif)
- [download_models.py](download_models.py)
- [download_models.sh](download_models.sh)

</details>



This document provides comprehensive instructions for setting up the FastPhotoStyle system on your machine. It covers system requirements, environment configuration, installation of dependencies, and downloading the necessary pre-trained models. For information about the algorithm itself, please see [Core Algorithm](#3).

## 1. System Requirements

FastPhotoStyle has specific hardware and software requirements to function properly:

```mermaid
graph TD
    subgraph "Hardware Requirements"
        H1["NVIDIA GPU"] --> H2["CUDA-Compatible"]
        H2 --> H3["Recommended: NVIDIA Titan"]
    end
    
    subgraph "Software Requirements"
        S1["Operating System"] --> S2["Ubuntu 16.04"]
        S3["CUDA"] --> S4["Version 9.1"]
        S5["Python"] --> S6["Python 2.7 or 3.5"]
        S7["Deep Learning Framework"] --> S8["PyTorch 0.4.0"]
    end
    
    H1 -.-> S3
```

Sources: [TUTORIAL.md:29-32](), [Dockerfile:1-6]()

## 2. Environment Setup

There are two ways to set up the FastPhotoStyle environment:

1. Native installation on your machine
2. Using Docker (recommended for reproducibility)

### 2.1 Option 1: Native Installation

#### 2.1.1 Setting Up Environment Variables

First, configure essential environment variables:

```bash
export ANACONDA=PATH-TO-YOUR-ANACONDA-LIBRARY
export CUDA_PATH=/usr/local/cuda
export PATH=${ANACONDA}/bin:${CUDA_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${ANACONDA}/lib:${CUDA_PATH}/bin64:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=${CUDA_PATH}/include
```

Sources: [TUTORIAL.md:33-39]()

#### 2.1.2 Installing System Dependencies

Install the required system packages:

```bash
sudo apt-get install -y axel imagemagick
```

Sources: [TUTORIAL.md:40-41](), [Dockerfile:7-22]()

#### 2.1.3 Installing Python Dependencies

Install the required Python packages:

```mermaid
flowchart TD
    A["PyTorch 0.4.0"] --> B["Base Dependencies"]
    B --> C["scikit-umfpack"]
    B --> D["setuptools"]
    B --> E["cupy"]
    B --> F["pynvrtc"]
    B --> G["OpenCV3"]
    
    subgraph "Installation Commands"
        CMD1["conda install pytorch=0.4.0 torchvision cuda91 -y -c pytorch"]
        CMD2["pip install scikit-umfpack"]
        CMD3["pip install -U setuptools"]
        CMD4["pip install cupy"]
        CMD5["pip install pynvrtc"]
        CMD6["conda install -c menpo opencv3"]
    end
    
    C -.-> CMD2
    D -.-> CMD3
    E -.-> CMD4
    F -.-> CMD5
    G -.-> CMD6
    A -.-> CMD1
```

Sources: [TUTORIAL.md:42-47](), [Dockerfile:26-31]()

### 2.2 Option 2: Docker Installation

Using Docker provides a more consistent environment. The repository includes a Dockerfile that sets up all dependencies.

#### 2.2.1 Building the Docker Image

```bash
docker build -t fastphotostyle:v1.0 .
```

#### 2.2.2 Running the Docker Container

```bash
docker run -v YOUR_PATH:YOUR_PATH --runtime=nvidia -i -t fastphotostyle:v1.0 /bin/bash
```

Sources: [TUTORIAL.md:199-209](), [Dockerfile:1-31]()

### 2.3 Installation Flowchart

The following diagram illustrates the complete installation process:

```mermaid
flowchart TD
    Start["Start Installation"] --> DecisionDocker{"Use Docker?"}
    
    DecisionDocker -->|"Yes"| DockerBuild["Build Docker Image"]
    DockerBuild --> DockerRun["Run Docker Container"]
    DockerRun --> DownloadModels
    
    DecisionDocker -->|"No"| SetupEnv["Setup Environment Variables"]
    SetupEnv --> InstallSystemDeps["Install System Dependencies"]
    InstallSystemDeps --> InstallPythonDeps["Install Python Dependencies"]
    InstallPythonDeps --> DownloadModels["Download Pre-trained Models"]
    
    DownloadModels --> TestInstall["Test Installation with Demo"]
    TestInstall --> End["Installation Complete"]
```

Sources: [TUTORIAL.md:29-47](), [TUTORIAL.md:199-209](), [Dockerfile:1-31]()

## 3. Downloading Pre-trained Models

FastPhotoStyle requires pre-trained models for the PhotoWCT module. These models can be downloaded using the provided scripts.

### 3.1 Using the Download Script

The repository includes a script for downloading the pre-trained models:

```bash
./download_models.sh
```

This script:
1. Runs `download_models.py` to fetch the models from Google Drive
2. Unzips the downloaded file (`models.zip`)

### 3.2 Manual Download (Alternative)

If the script doesn't work, you can manually download the models from the Google Drive link with ID: `1ENgQm9TgabE1R99zhNf5q6meBvX6WFuq`

```mermaid
graph LR
    A["download_models.py"] --> B["Download from Google Drive"]
    B --> C["models.zip"]
    C --> D["Unzip"]
    D --> E["Pre-trained Models"]
    
    subgraph "Model Components"
        E --> VGG1["vgg_normalised_conv1_1.t7"]
        E --> VGG2["vgg_normalised_conv2_1.t7"]
        E --> VGG3["vgg_normalised_conv3_1.t7"]
        E --> VGG4["vgg_normalised_conv4_1.t7"]
        E --> VGG5["vgg_normalised_conv5_1.t7"]
        E --> DEC1["decoder1.t7"]
        E --> DEC2["decoder2.t7"]
        E --> DEC3["decoder3.t7"]
        E --> DEC4["decoder4.t7"]
        E --> DEC5["decoder5.t7"]
    end
```

Sources: [download_models.py:1-35](), [download_models.sh:1-4]()

## 4. Verifying Installation

To ensure your installation is working correctly, run one of the demo examples provided in the repository.

### 4.1 Basic Demo

Run the basic demo without segmentation:

```bash
./demo_example1.sh
```

This will:
1. Create necessary directories
2. Download example content and style images
3. Resize the images to appropriate dimensions
4. Run the style transfer algorithm
5. Output the stylized image to the results folder

### 4.2 Fast Mode Demo

To run the faster approximation of the algorithm:

```bash
./demo_example1_fast.sh
```

Sources: [TUTORIAL.md:57-94]()

## 5. Installation Dependencies Graph

The following diagram shows the key components and dependencies of the FastPhotoStyle system:

```mermaid
graph TD
    subgraph "FastPhotoStyle System"
        PhotoWCT["PhotoWCT Module"] --> VGGEnc["VGG Encoders"]
        PhotoWCT --> VGGDec["VGG Decoders"]
        PhotoWCT --> WCTTransform["WCT Transform"]
        
        Smoothing["Smoothing Module"] --> PropagatorSmooth["Propagator Smoothing"]
        Smoothing --> GIFSmoothing["Guided Image Filtering"]
    end
    
    subgraph "Python Dependencies"
        PyTorch["PyTorch 0.4.0"]
        CuPy["CuPy"]
        OpenCV["OpenCV3"]
        ScikitUmfpack["scikit-umfpack"]
        PyNVRTC["pynvrtc"]
    end
    
    subgraph "System Dependencies"
        CUDA["CUDA 9.1"]
        Anaconda["Anaconda3"]
        Ubuntu["Ubuntu 16.04"]
        Axel["axel"]
        ImageMagick["imagemagick"]
    end
    
    VGGEnc --> PyTorch
    VGGDec --> PyTorch
    WCTTransform --> PyTorch
    WCTTransform --> CuPy
    PropagatorSmooth --> ScikitUmfpack
    GIFSmoothing --> OpenCV
    PyTorch --> CUDA
    CuPy --> CUDA
    PyNVRTC --> CUDA
```

Sources: [TUTORIAL.md:29-47](), [Dockerfile:1-31]()

## 6. Troubleshooting

### 6.1 Common Installation Issues

| Issue | Potential Cause | Solution |
|-------|-----------------|----------|
| CUDA version mismatch | Incompatible CUDA version | Install CUDA 9.1 specifically |
| PyTorch import errors | Incorrect PyTorch version | Ensure you have PyTorch 0.4.0 |
| Missing model files | Failed download | Download models manually and place in the models directory |
| GPU not detected | CUDA path issues | Check environment variables and ensure NVIDIA drivers are installed |
| OpenCV import errors | Missing dependencies | Install OpenCV3 with `conda install -c menpo opencv3` |

### 6.2 GPU Memory Requirements

For optimal performance, FastPhotoStyle requires a GPU with sufficient memory:

| Image Size | Minimum GPU Memory |
|------------|-------------------|
| 256x256 | 2 GB |
| 512x512 | 4 GB |
| 1024x1024 | 8 GB |
| 2048x2048 | 12+ GB |

For high-resolution images, you may need to resize them to fit within your GPU's memory constraints.

Sources: [TUTORIAL.md:31]()

## 7. Next Steps

After successful installation, you can proceed to learn about usage patterns. See [Usage Guide](#4) for more information on using FastPhotoStyle in different scenarios, including:

- Basic usage without segmentation
- Using the fast approximation mode
- Using segmentation for region-aware style transfer

Sources: [TUTORIAL.md:49-197]()

---

