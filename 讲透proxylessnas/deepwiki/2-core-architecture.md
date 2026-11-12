<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/proxylessnas · page 2 Core Architecture · fetched 2026-10-30 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/ProxylessNAS_iclr_poster_final.pdf](assets/ProxylessNAS_iclr_poster_final.pdf)

</details>



This document provides a technical deep dive into the ProxylessNAS system architecture, covering the search methodology, hardware specialization approach, and the modular design that enables direct neural architecture search without proxy tasks. For implementation details of the search algorithm, see [Neural Architecture Search Method](#2.1). For performance benchmarks and comparisons, see [Performance Comparisons](#2.2).

## System Overview

ProxylessNAS implements a direct neural architecture search system that optimizes architectures specifically for target hardware platforms without using proxy tasks. The system consists of four main architectural components that work together to enable hardware-aware architecture optimization.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Search Phase"
        A["/search/"] --> B["Architecture Search Engine"]
        B --> C["Hardware-Aware Optimization"]
        C --> D["Architecture Discovery"]
    end
    
    subgraph "Training Phase"
        E["/training/"] --> F["Model Training Pipeline"]
        D --> F
        F --> G["Trained Architectures"]
    end
    
    subgraph "Model Distribution"
        H["/proxyless_nas/"] --> I["proxyless_cpu()"]
        H --> J["proxyless_gpu()"]
        H --> K["proxyless_mobile()"]
        H --> L["proxyless_mobile_14()"]
        H --> M["proxyless_cifar()"]
        
        N["/proxyless_nas_tensorflow/"] --> O["tf_proxyless_cpu()"]
        N --> P["tf_proxyless_gpu()"]
        N --> Q["tf_proxyless_mobile()"]
        N --> R["tf_proxyless_mobile_14()"]
    end
    
    G --> H
    G --> N
    
    subgraph "External Interfaces"
        S["PyTorch Hub"] --> H
        T["Direct Import"] --> H
        U["TensorFlow Import"] --> N
    end
```

Sources: [README.md:100-106]()

The architecture follows a three-phase approach: search discovers optimal architectures for specific hardware, training produces high-quality models, and distribution provides easy access through multiple interfaces.

### Hardware Specialization Architecture

ProxylessNAS's core innovation is hardware-specific architecture optimization. Rather than using a single architecture across all platforms, the system generates specialized models optimized for different hardware constraints.

```mermaid
graph LR
    subgraph "Hardware Targets"
        A["CPU Optimization"] --> B["proxyless_cpu"]
        C["GPU Optimization"] --> D["proxyless_gpu"] 
        E["Mobile Optimization"] --> F["proxyless_mobile"]
        G["Mobile 1.4x Optimization"] --> H["proxyless_mobile_14"]
        I["CIFAR Optimization"] --> J["proxyless_cifar"]
    end
    
    subgraph "Framework Support"
        B --> K["/proxyless_nas/model_zoo.py"]
        D --> K
        F --> K 
        H --> K
        J --> K
        
        B --> L["/proxyless_nas_tensorflow/model_zoo.py"]
        D --> L
        F --> L
        H --> L
    end
    
    subgraph "Deployment Interfaces"
        K --> M["torch.hub.load()"]
        K --> N["Direct Import"]
        L --> O["TensorFlow Import"]
    end
```

Sources: [README.md:27-28](), [README.md:77-87]()

Each hardware specialization produces a distinct architecture optimized for specific latency, energy, and accuracy trade-offs. The `proxyless_cpu` targets Intel CPU platforms, `proxyless_gpu` optimizes for GPU inference, while `proxyless_mobile` and `proxyless_mobile_14` focus on mobile deployment scenarios.

## Direct Search Methodology

The system implements a direct neural architecture search approach that eliminates proxy tasks. Traditional NAS methods use proxy datasets or reduced training to estimate architecture performance, but ProxylessNAS searches directly on the target task and hardware.

### Search-to-Deployment Pipeline

```mermaid
graph TD
    subgraph "Direct Search Process"
        A["Target Task Input"] --> B["Hardware Profile Input"]
        B --> C["/search/ - Architecture Search"]
        C --> D["Direct Performance Measurement"]
        D --> E["Architecture Optimization"]
        E --> F["Optimal Architecture Discovery"]
    end
    
    subgraph "Training Pipeline"  
        F --> G["/training/ - Model Training"]
        G --> H["Full Training on Target Task"]
        H --> I["Performance Validation"]
    end
    
    subgraph "Model Production"
        I --> J["Model Serialization"]
        J --> K["PyTorch Model (.pth)"]
        J --> L["TensorFlow Model (.h5)"]
    end
    
    subgraph "Distribution"
        K --> M["proxyless_nas package"]
        L --> N["proxyless_nas_tensorflow package"] 
        M --> O["torch.hub integration"]
        M --> P["Direct import access"]
        N --> Q["TensorFlow import access"]
    end
```

Sources: [README.md:22](), [README.md:102-105]()

This direct approach ensures that the discovered architectures are optimized for actual deployment conditions rather than proxy metrics that may not correlate with real-world performance.

## Modular Framework Design

The system uses a modular design that separates search, training, and deployment concerns while supporting multiple deep learning frameworks.

### Component Interaction Architecture

```mermaid
graph TB
    subgraph "Core Search Engine"
        A["/search/"] --> B["search_config.py"]
        B --> C["architecture_space.py"]
        C --> D["search_algorithm.py"]
        D --> E["hardware_profiler.py"]
    end
    
    subgraph "Training Infrastructure"
        F["/training/"] --> G["training_config.py"]
        G --> H["model_trainer.py"]
        H --> I["validation_metrics.py"]
    end
    
    subgraph "Model Interfaces"
        J["/proxyless_nas/"] --> K["__init__.py"]
        K --> L["model_zoo.py"]
        L --> M["proxyless_cpu()"]
        L --> N["proxyless_gpu()"]
        L --> O["proxyless_mobile()"]
        
        P["/proxyless_nas_tensorflow/"] --> Q["__init__.py"]
        Q --> R["model_zoo.py"] 
        R --> S["tf_proxyless_cpu()"]
        R --> T["tf_proxyless_gpu()"]
        R --> U["tf_proxyless_mobile()"]
    end
    
    subgraph "External Integration"
        V["hubconf.py"] --> M
        V --> N
        V --> O
        W["eval.py"] --> M
        X["eval_tf.py"] --> S
    end
    
    E --> G
    I --> L
    I --> R
```

Sources: [README.md:77-97]()

The modular design allows each component to operate independently while maintaining clear interfaces. The search engine discovers architectures, the training infrastructure produces models, and the model interfaces provide framework-specific access patterns.

## Hardware-Aware Optimization

ProxylessNAS implements hardware-aware optimization by directly measuring latency and resource usage on target hardware during the search process. This eliminates the accuracy gap between proxy metrics and actual deployment performance.

### Hardware Profiling Integration

```mermaid
graph LR  
    subgraph "Target Hardware"
        A["Intel CPU"] --> B["CPU Profiler"]
        C["NVIDIA GPU"] --> D["GPU Profiler"] 
        E["Mobile ARM"] --> F["Mobile Profiler"]
        G["Edge Devices"] --> H["Edge Profiler"]
    end
    
    subgraph "Architecture Search"
        I["Architecture Candidate"] --> J["Hardware Measurement"]
        B --> J
        D --> J
        F --> J  
        H --> J
        J --> K["Latency Measurement"]
        J --> L["Memory Usage"]
        J --> M["Energy Consumption"]
    end
    
    subgraph "Optimization Loop"
        K --> N["Performance Score"]
        L --> N
        M --> N
        N --> O["Architecture Update"]
        O --> I
    end
    
    subgraph "Specialized Outputs"
        N --> P["proxyless_cpu - Intel optimized"]
        N --> Q["proxyless_gpu - GPU optimized"] 
        N --> R["proxyless_mobile - ARM optimized"]
    end
```

Sources: [README.md:67-72]()

This hardware-aware approach produces architectures that achieve optimal trade-offs between accuracy and efficiency for specific deployment targets, as demonstrated by the performance improvements shown in the repository's benchmarks.

---

