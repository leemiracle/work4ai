<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/computervision-recipes · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [environment.yml](environment.yml)
- [scenarios/README.md](scenarios/README.md)
- [scenarios/classification/README.md](scenarios/classification/README.md)
- [scenarios/media/figures.pptx](scenarios/media/figures.pptx)
- [scenarios/media/intro_ic_vis.jpg](scenarios/media/intro_ic_vis.jpg)
- [scenarios/media/intro_is_vis.jpg](scenarios/media/intro_is_vis.jpg)
- [scenarios/media/intro_iseg_vis.jpg](scenarios/media/intro_iseg_vis.jpg)
- [scenarios/media/intro_kp_vis.jpg](scenarios/media/intro_kp_vis.jpg)
- [scenarios/media/intro_od_vis.jpg](scenarios/media/intro_od_vis.jpg)

</details>



This document provides a comprehensive introduction to the Microsoft Computer Vision Recipes repository, a collection of tools, examples, and best practices for building computer vision systems.

## Purpose and Scope

The Computer Vision Recipes repository aims to accelerate the development of computer vision solutions by providing ready-to-use components and examples. Rather than implementing algorithms from scratch, it draws from state-of-the-art libraries while adding utilities for data loading, model optimization, evaluation, and cloud deployment. The repository focuses on providing practical guidance for solving common computer vision tasks like classification, detection, similarity, segmentation, action recognition, and tracking.

The goal is to significantly reduce development time by simplifying the journey from defining a business problem to implementing a production-ready solution. This is achieved through extensively documented example notebooks and reusable utility functions, all built on PyTorch.

Sources: [README.md:10-14]()

## Repository Structure

The repository is organized into four main components:

```mermaid
graph TD
    A["Microsoft Computer Vision Recipes"] --> B["scenarios/"]
    A --> C["utils_cv/"]
    A --> D["contrib/"]
    A --> E["tests/"]
    
    B --> B1["classification/"]
    B --> B2["detection/"]
    B --> B3["similarity/"]
    B --> B4["segmentation/"] 
    B --> B5["action_recognition/"]
    B --> B6["tracking/"]
    
    C --> C1["common/"]
    C --> C2["classification/"]
    C --> C3["detection/"]
    C --> C4["similarity/"]
    C --> C5["segmentation/"]
    C --> C6["action_recognition/"]
    C --> C7["tracking/"]
    
    D --> D1["crowd_counting/"]
    D --> D2["action_recognition_i3d/"]
    D --> D3["html_demo/"]
    D --> D4["vm_builder/"]
    
    E --> E1["Unit Tests"]
    E --> E2["Integration Tests"]
</mermaid>

- **scenarios/**: Jupyter notebooks demonstrating how to implement different computer vision tasks, serving as both tutorials and examples.
- **utils_cv/**: Core Python utility library containing reusable functions and classes for each computer vision scenario.
- **contrib/**: Community contributions showcasing additional applications and implementations.
- **tests/**: Testing infrastructure to ensure code quality and reliability.

Sources: [README.md:15-16](), [README.md:46-61]()

## Supported Computer Vision Tasks

The repository covers several key computer vision scenarios, each with its own set of utilities, examples, and best practices:

```mermaid
graph TD
    A["Computer Vision Tasks"] --> B["Image Classification"]
    A --> C["Object Detection"]
    A --> D["Image Similarity"]
    A --> E["Segmentation"]
    A --> F["Action Recognition"]
    A --> G["Multi-Object Tracking"]
    
    B -->|"identifies categories"| B1["ClassificationLearner"]
    C -->|"locates objects"| C1["DetectionLearner"]
    D -->|"finds similar images"| D1["compute_feature()"]
    E -->|"classifies each pixel"| E1["Segmentation"]
    F -->|"identifies video actions"| F1["VideoLearner"]
    G -->|"tracks objects over time"| G1["TrackingLearner"]
</mermaid>

1. **Image Classification**: Identifies what object is present in an image, typically requiring objects to be reasonably large.
2. **Object Detection**: Identifies and locates (with bounding boxes) which objects are present in an image, useful for finding small objects.
3. **Image Similarity**: Given an input image, finds similar objects in a reference dataset.
4. **Segmentation**: Assigns a category to every pixel in an image (e.g., background, bottle, hand, sky).
5. **Action Recognition**: Identifies what actions are performed in video footage (e.g., "running", "opening a bottle") and their start/end times.
6. **Multi-Object Tracking**: Detects and tracks multiple objects in a video sequence over time.

Sources: [README.md:50-58](), [scenarios/README.md:14-37]()

## Development Workflow

The repository supports a complete workflow for developing computer vision solutions:

```mermaid
graph LR
    A["Data Preparation"] --> B["Model Training"]
    B --> C["Evaluation"]
    C --> D["Deployment"]
    
    A --> A1["Dataset Loading"]
    A --> A2["Data Augmentation"]
    A --> A3["Transforms"]
    
    B --> B1["Parameter Sweeping"]
    B --> B2["Fine-tuning"]
    B --> B3["Training Loops"]
    
    C --> C1["Metrics Calculation"]
    C --> C2["Visualization"]
    C --> C3["Validation"]
    
    D --> D1["Azure Container Instances"]
    D --> D2["Azure Kubernetes Service"]
    D --> D3["Model Serving"]
</mermaid>

This workflow includes:
1. **Data Preparation**: Tools for loading, transforming, and augmenting image data
2. **Model Training**: Utilities for training models, including parameter sweeping and fine-tuning
3. **Evaluation**: Methods for calculating metrics and visualizing results
4. **Deployment**: Integration with Azure services for deploying models

Sources: [README.md:77-82](), [scenarios/classification/README.md:38-52]()

## Core Components

The repository centers around two main technical components:

### 1. Utility Library (utils_cv)

```mermaid
graph TD
    A["utils_cv"] --> B["utils_cv.common"]
    A --> C["utils_cv.classification"]
    A --> D["utils_cv.detection"]
    A --> E["utils_cv.similarity"]
    A --> F["utils_cv.segmentation"]
    A --> G["utils_cv.action_recognition"]
    A --> H["utils_cv.tracking"]
    
    B --> B1["GPU Utilities"]
    B --> B2["Config Handling"]
    B --> B3["Data Helpers"]
    
    C --> C1["ClassificationLearner"]
    C --> C2["ParameterSweeper"]
    
    D --> D1["DetectionLearner"]
    D --> D2["DetectionDataset"]
    
    E --> E1["compute_feature()"]
    E --> E2["ComparativeSet"]
    
    G --> G1["VideoLearner"]
    G --> G2["VideoDataset"]
    
    H --> H1["TrackingLearner"]
    H --> H2["FairMOT"]
</mermaid>

The utils_cv package provides reusable components for each computer vision task with:
- Data loading and processing utilities
- Model training and evaluation classes
- Visualization tools
- Deployment helpers

### 2. Scenario Notebooks

The notebooks in the scenarios directory demonstrate how to:
- Load and prepare data
- Train and evaluate models
- Visualize results
- Deploy models to production
- Optimize performance

Each scenario (classification, detection, etc.) has its own set of notebooks covering basic to advanced topics.

Sources: [README.md:16](), [scenarios/classification/README.md:25-38]()

## Azure Integration

The repository includes extensive integration with Azure services for training and deployment:

```mermaid
graph TD
    A["Computer Vision Solution"] --> B["Training"]
    A --> C["Deployment"]
    
    B --> B1["Local Training"]
    B --> B2["AzureML Training"]
    B2 --> B21["HyperDrive Parameter Sweeping"]
    B2 --> B22["GPU Compute"]
    
    C --> C1["Azure Container Instances"]
    C --> C2["Azure Kubernetes Service"]
    
    C1 --> D1["REST API Endpoint"]
    C2 --> D1
</mermaid>

Key Azure integrations include:
- **Azure Machine Learning service**: For scalable training and experiment tracking
- **Azure Container Instances**: For low-scale, CPU-based model deployment
- **Azure Kubernetes Service**: For high-scale production deployments with autoscaling

These integrations provide a path from experimentation to production deployment.

Sources: [README.md:77-82](), [scenarios/classification/README.md:40-52]()

## Getting Started

To begin using the repository:

1. Set up the environment by following the instructions in [SETUP.md](README.md:37)
2. Navigate to the [scenarios](scenarios/) folder to explore example notebooks
3. Start with the classification notebooks, which introduce concepts used by other scenarios
4. For a quick overview without setup, try the Binder option

The repository supports both Windows and Linux, though performance is generally better on Linux with GPU acceleration.

Sources: [README.md:35-40](), [environment.yml:1-46]()

## Target Audience

The repository is designed for:
- Data scientists and machine learning engineers with varying levels of computer vision expertise
- Developers looking to implement custom machine learning models for vision problems
- Researchers exploring state-of-the-art computer vision techniques

Sources: [README.md:31-33]()

## Alternative Solutions

For certain computer vision problems, you may not need to build custom models. Microsoft offers pre-built solutions:

- **Vision Services**: Pre-trained REST APIs for image tagging, face recognition, OCR, and more
- **Custom Vision**: A SaaS service to train and deploy models with minimal ML expertise

Consider these options before developing custom solutions for simpler use cases.

Sources: [README.md:63-74]()

---

